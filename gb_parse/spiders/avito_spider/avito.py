import scrapy
from avito_xpath_selectors import PAGINATION, ADVT


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/perm/kvartiry/prodam']

    def _get_follow(self, response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    def parse(self, response):
        for item in PAGINATION, ADVT:
            yield from self._get_follow(response, item["selector"], item["callback"])

    def advt_parse(self, response):
        print(1)

