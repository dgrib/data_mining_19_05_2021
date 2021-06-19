import scrapy
import json


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com', 'instagram.com']  # Это разные домены
    start_urls = ['https://www.instagram.com/accounts/login/']
    _login_path = '/accounts/login/ajax/'
    _tags_path = '/explore/tags/{tag}/'

    def __init__(self, login, password, tags, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            # так как будет делать отправку запроса поэтому yield, будем отправлять какуюто форму
            # указали на какой url должен происходить запрос, методом.. , колбэк какой будет обрабатывать ответ
            yield scrapy.FormRequest(
                response.urljoin(self._login_path),
                method='POST',
                callback=self.parse,
                formdata={
                    "username": self.login,
                    "enc_password": self.password,
                    # остальные параметры не влияют на авторизацию
                },
                headers={
                    'X-CSRFToken': js_data['config']['csrf_token'],
                }
            )
        except AttributeError:
            r_data = response.json()
            # response.json()
            # {'user': True, 'userId': '47841367410', 'authenticated': True, 'oneTapPrompt': True, 'status': 'ok'}
            if r_data.get("authenticated"):
                for tag in self.tags:
                    url = self._tags_path.format(tag=tag)
                    yield response.follow(url, callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        print(1)

    def js_data_extract(self, response):
        js = response.xpath("//script[contains(text(), 'window._sharedData')]/text()").extract_first()
        start_idx = js.find('{')
        data = json.loads(js[start_idx: -1])
        return data

