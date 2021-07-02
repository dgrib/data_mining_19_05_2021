import scrapy
from .avito_xpath_selectors import ADVT
from .avito_loaders import AvitoRealEstateLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/perm/nedvizhimost']

    def parse(self, response):
        yield response.follow(
            response.xpath("//a[@data-category-id='24'][@title='Все квартиры']/@href").get(),
            callback=self.apartment_parse,
            )

    def apartment_parse(self, response, paginate=True):
        for url in response.xpath(ADVT['selector']):
            yield response.follow(url, getattr(self, ADVT['callback']))

        # если меньше 100 страниц будет, то ошибка и скрапи проигнорирует ее
        # [] for увидит пустой список и пройдет мимо него, итерации по пустому списку не происходит
        for page_num in range(2, 101) if paginate else []:
            yield response.follow(f'?p={page_num}', callback=self.parse, cb_kwargs={'paginate': False})

    def advt_parse(self, response):
        loader = AvitoRealEstateLoader(response=response)  # отдаем лоадеру response, лоадер в ините все делает
        yield loader.load_item()

