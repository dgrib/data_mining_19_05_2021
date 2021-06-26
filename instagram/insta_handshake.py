import copy

import scrapy
import json
from urllib.parse import urlencode


class InstaHandshakeSpider(scrapy.Spider):
    name = 'insta_handshake'
    allowed_domains = ['www.instagram.com', 'instagram.com', 'i.instagram.com']
    start_urls = ['https://www.instagram.com/accounts/login/']
    _login_path = '/accounts/login/ajax/'
    _api_following = 'https://i.instagram.com/api/v1/friendships/{user_id}/following/'
    _api_followers = 'https://i.instagram.com/api/v1/friendships/{user_id}/followers/'
    _token = None
    following_ids = set()

    api_followers_params = {
        'count': 12,
        # 'max_id': None,
        'search_surface': 'follow_list_page',
    }

    api_following_params = {
        'count': 12,
        # 'max_id': None,
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
                # for tag in self.tags:
                #     url = self._tags_path.format(tag=tag)
                yield response.follow(f'/{self.user_1}/', callback=self.user_1_parse)

    def js_data_extract(self, response):
        js = response.xpath("//script[contains(text(), 'window._sharedData')]/text()").extract_first()
        start_idx = js.find('{')
        data = json.loads(js[start_idx: -1])
        return data

    def user_1_parse(self, response):
        js_data = self.js_data_extract(response)
        user_id = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']  # +
        self._token = js_data['config']['csrf_token']  # +
        params = copy.copy(self.api_following_params)  # +
        yield response.follow(
            # 'https://i.instagram.com/api/v1/friendships/305701719/followers/?count=12&search_surface=follow_list_page',
            self._api_following.format(user_id=user_id) + '?' + urlencode(params),
            # cookies=response.request.cookies,
            headers={
                # 'X-CSRFToken': self._token,
                'X-IG-App-ID': '936619743392459',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                # 'x-ig-set-www-claim': 'hmac.AR2sTVIYz2L-PYUhyVqqU7JHTlmLq1dNdiqDBlSQcIcfrYTl'
            },
            callback=self.user_parse,
            cb_kwargs={
                'user_id': user_id,
                'quit_marker': False,
            },
        )

    def user_parse(self, response, **cb_kwargs):
        if cb_kwargs['quit_marker']:  # закончилась пегинация
            yield self.next_user()
        else:
            js = response.json()
            # наполняем множество following
            for user in js['users']:
                self.following_ids.add((user.get('pk'), user['username']))
            params = copy.copy(self.api_following_params)
            params['max_id'] = js['next_max_id']
            quit_marker = True if not js['big_list'] else False  # False если меньше 12 пользователей приходит
            yield response.follow(
                self._api_following.format(user_id=cb_kwargs['user_id']) + '?' + urlencode(params),
                # cookies=response.request.cookies,
                headers={
                    # 'X-CSRFToken': self._token,
                    'X-IG-App-ID': '936619743392459',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                    # 'x-ig-set-www-claim': 'hmac.AR2sTVIYz2L-PYUhyVqqU7JHTlmLq1dNdiqDBlSQcIcfrYTl'
                },
                callback=self.user_parse,
                cb_kwargs={
                    'user_id': cb_kwargs['user_id'],
                    'quit_marker': quit_marker,
                },
            )

    def next_user(self):
        print(1)