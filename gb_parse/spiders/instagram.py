import datetime
from urllib.parse import urlencode

import scrapy
import json


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com', 'instagram.com', 'i.instagram.com']  # Это разные домены
    start_urls = ['https://www.instagram.com/accounts/login/']
    _login_path = '/accounts/login/ajax/'
    _tags_path = '/explore/tags/{tag}/'
    _api_url = '/api/v1/tags/{tag}/sections/'
    token = None

    def __init__(self, login, password, tags, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

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
                for tag in self.tags:
                    url = self._tags_path.format(tag=tag)
                    yield response.follow(url, callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        js_data = self.js_data_extract(response)
        insta_tag = InstaTag(js_data['entry_data']['TagPage'][0]['data'])
        self.token = js_data['config']['csrf_token']  # перезаписываем, так как хз - меняется или нет
        yield insta_tag.get_tag_item()  # структура Tag
        yield from insta_tag.get_first_page_items()  # собрать статьи с начальной страницы
        # pagination
        yield scrapy.FormRequest(
            'https://i.instagram.com/api/v1/tags/python/sections/',
            formdata={
                'include_persistent': "0",
                'max_id': insta_tag.variables['max_id'],
                'page': str(insta_tag.variables['page']),
                'surface': "grid",
                'tab': "recent",
            },
            method='POST',
            cookies=response.request.cookies,
            headers={
                'X-CSRFToken': self.token,
                # TODO вытащить из request X-IG-App-ID
                'X-IG-App-ID': '936619743392459',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            },
            callback=self._api_page_parse,
        )

    def _api_page_parse(self, response):
        js_data = response.json()
        insta_item = InstaOtherPageItem(js_data)
        yield from insta_item.get_other_page_items()  # собрать статьи со 2,3... страниц
        yield scrapy.FormRequest(
            'https://i.instagram.com/api/v1/tags/python/sections/',
            formdata={
                'include_persistent': "0",
                'max_id': insta_item.variables['max_id'],
                'page': str(insta_item.variables['page']),
                'surface': "grid",
                'tab': "recent",
            },
            method='POST',
            cookies=response.request.cookies,
            headers={
                'X-CSRFToken': self.token,
                'X-IG-App-ID': '936619743392459',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            },
            callback=self._api_page_parse,
        )

    def js_data_extract(self, response):
        js = response.xpath("//script[contains(text(), 'window._sharedData')]/text()").extract_first()
        start_idx = js.find('{')
        data = json.loads(js[start_idx: -1])
        return data


class InstaTag:
    def __init__(self, tag_data: dict):
        self.variables = {
            "tag_name": tag_data['name'],
            "page": tag_data['recent']['next_page'],
            "max_id": tag_data['recent']['next_max_id'],
        }
        self.tag_data = tag_data

    def get_tag_item(self):
        item = dict()
        item['item_type'] = 'tag'
        item['date_parse'] = datetime.datetime.utcnow()
        data = {}
        for key, value in self.tag_data.items():
            if not (isinstance(value, dict) or isinstance(value, list)):
                data[key] = value
        item["data"] = data
        return item

    def get_first_page_items(self):
        for section in self.tag_data['recent']['sections']:
            for media in section['layout_content']['medias']:
                yield dict(date_parse=datetime.datetime.utcnow(), data=media['media'], item_type='article')

    def get_other_page_items(self):
        for section in self.tag_data['sections']:
            for media in section['layout_content']['medias']:
                yield dict(date_parse=datetime.datetime.utcnow(), data=media['media'], item_type='article')


class InstaOtherPageItem(InstaTag):
    def __init__(self, tag_data: dict):
        # super().__init__(tag_data)
        self.variables = {
            "page": tag_data['next_page'],
            "max_id": tag_data['next_max_id'],
        }
        self.tag_data = tag_data
