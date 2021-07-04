import copy
from urllib import response as resp

import scrapy
import json
from urllib.parse import urlencode
from .settings import BOT_NAME
from pymongo import MongoClient
"""
Идея:
1. following в инсте не более 5к - собираю их и сравниваю с followers - получаю список взаимных друзей первого польз.
2. Заношу в базу (монго) как пользователя 0 порядка и список его друзей.
3. Из списка друзей - беру пользователей (1 порядок) и ищу их взаимных друзей.
4. Прохожу по списку друзей 1 порядка и формирую список друзей 2 порядка.
5. Номер порядка и friend_path (цепочка id от начального до текущего пользователя) 
    проставляю в каждом пользователе в базе.
6. Так - пока не найду совпадение со вторым введенным пользователем.
7. Получаю цепочку имен по цепочке id во friend_path.
"""


class InstaHandshakeSpider(scrapy.Spider):
    name = 'insta_handshake'
    allowed_domains = ['www.instagram.com', 'instagram.com', 'i.instagram.com']
    start_urls = ['https://www.instagram.com/accounts/login/']
    _login_path = '/accounts/login/ajax/'
    _api_following = 'https://i.instagram.com/api/v1/friendships/{user_id}/following/'
    _api_followers = 'https://i.instagram.com/api/v1/friendships/{user_id}/followers/'
    _token = None
    following_ids = set()
    friends = set()

    api_followers_params = {
        'count': 12,
        'search_surface': 'follow_list_page',
    }

    api_following_params = {
        'count': 12,
    }

    def __init__(self, login, password, user_1, user_2, *args, **kwargs):
        super(InstaHandshakeSpider, self).__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.user_1 = user_1
        self.user_2 = user_2

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                response.urljoin(self._login_path),
                method='POST',
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password, },
                headers={'X-CSRFToken': js_data['config']['csrf_token'], },
            )
        except AttributeError:
            r_data = response.json()
            if r_data.get("authenticated"):
                cb_kwargs = dict()
                cb_kwargs['generation'] = 0
                cb_kwargs['handshake_path'] = []  # хранит цепочку друзей и добавляет к ней нового пользоваателя
                cb_kwargs['handshake_path'].append(self.user_1)

                yield response.follow(f'/{self.user_1}/', callback=self.prepare_user_following, cb_kwargs=cb_kwargs)

    def js_data_extract(self, response):
        js = response.xpath("//script[contains(text(), 'window._sharedData')]/text()").extract_first()
        start_idx = js.find('{')
        data = json.loads(js[start_idx: -1])
        return data

    def prepare_user_following(self, response, **cb_kwargs):
        """Собирает данные со страницы пользователя и делает запрос на API"""
        js_data = self.js_data_extract(response)
        user_id = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        self._token = js_data['config']['csrf_token']
        params = copy.copy(self.api_following_params)
        yield response.follow(
            self._api_following.format(user_id=user_id) + '?' + urlencode(params),
            headers={
                'X-IG-App-ID': '936619743392459',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            },
            callback=self.following_count,
            cb_kwargs={
                'user_id': user_id,
                'quit_marker': False,
                'generation': cb_kwargs['generation'],
                'handshake_path': cb_kwargs['handshake_path'],
            },
        )

    def following_count(self, response, **cb_kwargs):
        """Наполняет множество following_ids"""
        if cb_kwargs['quit_marker']:  # если закончилась пегинация, выходим
            params = self.api_followers_params
            yield response.follow(
                self._api_followers.format(user_id=cb_kwargs['user_id']) + '?' + urlencode(params),
                callback=self.get_user_friends,
                headers={
                    'X-IG-App-ID': '936619743392459',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                },
                cb_kwargs={
                    'user_id': cb_kwargs['user_id'],
                    'quit_marker': False,
                    'generation': cb_kwargs['generation'],
                    'handshake_path': cb_kwargs['handshake_path'],
                },
            )
        else:
            js = response.json()
            # наполняем множество following_ids
            for user in js['users']:
                self.following_ids.add((user.get('pk'), user.get('username')))
            params = copy.copy(self.api_following_params)
            params['max_id'] = js.get('next_max_id', None)
            quit_marker = True if not js['big_list'] else False  # False если меньше 12 пользователей приходит
            yield response.follow(
                self._api_following.format(user_id=cb_kwargs['user_id']) + '?' + urlencode(params),
                headers={
                    'X-IG-App-ID': '936619743392459',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                },
                callback=self.following_count,
                cb_kwargs={
                    'user_id': cb_kwargs['user_id'],
                    'quit_marker': quit_marker,
                    'generation': cb_kwargs['generation'],
                    'handshake_path': cb_kwargs['handshake_path'],
                },
            )

    def get_user_friends(self, response, **cb_kwargs):
        """получает followers по 12, если из них ктото есть в following - то считаем их взаимно-друзьями"""
        if cb_kwargs['quit_marker']:
            insta_user = InstaUser(self.friends, **cb_kwargs)
            yield from insta_user.get_user_item()
            # mongo_reader = MongoReader()
            for response, cb_kwargs in self.read_next_user_generation(
                response,
                generation=cb_kwargs['generation'],
                handshake_path=cb_kwargs['handshake_path'],
            ):
                yield response.follow(
                    response.url,
                    callback=self.prepare_user_following,
                    cb_kwargs=cb_kwargs,
                )
            # yield from self.read_next_user_generation(
            #     response,
            #     generation=cb_kwargs['generation'],
            #     handshake_path=cb_kwargs['handshake_path'],
            # )
            # yield from self.read_next_user_generation()
            # до from ругался ERROR: Spider must return request, item, or None, got 'generator'

        else:
            js = response.json()
            # наполняем множество friends
            for user in js['users']:
                user_set = (user.get('pk'), user.get('username'))
                if user_set in self.following_ids:
                    # if user.get('username') == self.user_2:  # вывести цепочку друзей - если нашли user_2
                    #     return
                    self.friends.add(user_set)  # заменить на словарь ????? в базе лучше словарь, чем set

            params = copy.copy(self.api_followers_params)
            params['max_id'] = js.get('next_max_id', None)
            quit_marker = True if not js['big_list'] else False  # False если меньше 12 пользователей приходит
            yield response.follow(
                self._api_followers.format(user_id=cb_kwargs['user_id']) + '?' + urlencode(params),
                headers={
                    'X-IG-App-ID': '936619743392459',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                },
                callback=self.get_user_friends,
                cb_kwargs={
                    'user_id': cb_kwargs['user_id'],
                    'quit_marker': quit_marker,
                    'generation': cb_kwargs['generation'],
                    'handshake_path': cb_kwargs['handshake_path'],
                },
            )

    def read_next_user_generation(self, response, generation, handshake_path):
        """Читает из базы всех друзей определенного поколения"""
        client = MongoClient()
        db = client[BOT_NAME]

        collection_name = f"{self.name}"
        for item in db[collection_name].find({'friend_generation': generation}):
            for friend in item['friends_dict']:
                cb_kwargs = dict()
                cb_kwargs['user_id'] = friend[0]
                cb_kwargs['user_name'] = friend[1]
                cb_kwargs['generation'] = generation + 1
                cb_kwargs['handshake_path'] = copy.copy(handshake_path).append(friend[0])

                url = f'/https://www.instagram.com/{friend[1]}/'

                response = scrapy.http.Response(url)

                yield response, cb_kwargs
                #     response.follow(
                #     url,
                #     callback=self.prepare_user_following,
                #     cb_kwargs=cb_kwargs,
                # )
            print(2)
        print(1)


class InstaUser:
    def __init__(self, friends, **cb_kwargs):
        self.user_id = cb_kwargs['user_id']
        # self.handshake_path = [cb_kwargs['user_id'], ]
        self.handshake_path = cb_kwargs['handshake_path']
        self.generation = cb_kwargs['generation']
        self.friends_set = *friends,  # хз почему приходит tuple вместо set, пришлось сделать *

    def get_user_item(self, ):
        item = dict()
        item['user_id'] = self.user_id
        item['handshake_path'] = self.handshake_path
        item['friend_generation'] = self.generation
        item['friends_dict'] = self.friends_set
        yield item


# class MongoReader:
#     def __init__(self):
#         client = MongoClient()
#         self.db = client[BOT_NAME]
#
#     def read_next_user_generation(self, response, generation=0):
#         """Читает из базы всех друзей определенного поколения"""
#         collection_name = f"{InstaHandshakeSpider.name}"
#         for item in self.db[collection_name].find({'friend_generation': generation}):
#             for friend in item['friends_dict']:
#                 cb_kwargs = dict()
#                 cb_kwargs['user_name'] = friend[0]
#                 cb_kwargs['user_name'] = friend[1]
#                 cb_kwargs['generation'] = generation + 1
#                 cb_kwargs['handshake_path'].append(friend[0])
#
#                 yield response.follow(
#                     f'/{friend[1]}/',
#                     callback=InstaHandshakeSpider.prepare_user_following,
#                     cb_kwargs=cb_kwargs,
#                 )
#                 print(item['user_id'])
#             print(1)
#             # сделать yield всех друзей определенного поколения - заполнить базу их друзьями, поколение + 1
#         # yield read_next_user_generation(следующее поколение)
#         print(1)
