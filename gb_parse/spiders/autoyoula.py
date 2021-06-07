import pymongo
import scrapy
from .xpath_selectors import BRANDS, CARS, PAGINATION, CAR_DATA
from gb_parse.loaders import AutoyoulaLoader
# находит сылку , переходит по ней или находится на странице из которой нужны данные -
# отдает эту страницу обработчику лоадеру, лоадер закончил работу - я отдаю эти данные в пл
# паук д переходить по страницам и передавать лоадеру - вот щас ты должен отсбда грузить данные -
# собери item и передай его на пл, больше паук ничего не делает.
# не д думать о структурах данных, о том как ему сохранить в БД

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector_str, callback):
        for a_link in response.xpath(selector_str):  # будем иттерироваться по селекторам - скраппи это умеет
            yield response.follow(a_link, callback=callback)  # follow увидит что это селектор
            # и в data он содержит ссылку и follow сделает из него get() и извлечет ссылку
            # в скрапи лучше использовать xpath, нативно работает с селекторами
    # response.xpath("//div[@class='TransportMainFilters_brandsList__2tIkv']")
    # response.xpath("//div[@class='TransportMainFilters_brandsList__2tIkv']//a[@data-target='brand']")
    # response.xpath("//div[@class='TransportMainFilters_brandsList__2tIkv']//a[@data-target='brand']/@href")
    # response.xpath("//a[@data-target='brand']/../@class") переход вверх две точки как в терминале
    # __2tIkv - это суффиксы, фреймворки ставят их для борьбы с кешированием браузеров, на класснеймы,
    # чтобы при пересборке фронтэнда выкатки новой верссии - они поменялись и браузер сбросил все кеши.
    # для нас опасно если этот суффикс поменяется и парсер перестанет работать
    # response.xpath("//div[contains(@class, 'Filters_brandsList')]")
    # зная текст можно находить объект в котором он содержится
    # response.xpath("//div[contains(@class, 'Filters_brandsList')]//a[contains(text(), 'Audi')]")
    # response.xpath("//div[contains(@class, 'Filters_brandsList')]//a[contains(text(), 'Audi')]/@href").extract()

    def parse(self, response):
        yield from self._get_follow(
            response,
            BRANDS["selector"],
            getattr(self, BRANDS["callback"])
        )

    def brand_parse(self, response):
        for item in (PAGINATION, CARS):
            yield from self._get_follow(response, item["selector"], getattr(self, item["callback"]))

    # def car_parse(self, response):
    #     loader = AutoyoulaLoader(response=response)
    #     loader.add_value("url", response.url)
    #     for key, value in CAR_DATA.items():
    #         loader.add_value(key, value)
    #     # loader.load_item() возвращает экз класса обозначенного у него в default_item_class
    #     # изменили CAR_DATA вставили  "title": {"xpath": "//div[@data-target='advert-title']/text()"},
    #     # изза этого поменяли car_parse

    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        for key, value in CAR_DATA.items():
            loader.add_xpath(field_name=key, **value)
        # loader.load_item() возвращает экз класса обозначенного у него в default_item_class
        # Далее надо сохранять - но сохранять внутри паука и работать с БД внутри паука (на запись особенно) ПЛОХО !!!
        # для этого нужен отдельный слой. Если лоадер - это слой обработки респонза и извлечения конечных данных -
        # есть структура и передем данрные на пайплайн - некий конечный процесс обработки этой структуры -
        # куда и входит сохранение - чтобы отправить на пайплайн данные - делаем:
        yield loader.load_item()  # load_item вщзвращает нам класс словарь - default_item_class = dict
        # yield в управляющий процесс нам это все вернет, управляющий процесс увидит что этословарь или
        # что это объект scrapy.item и передаст это на пайплайн - надо сделать пайплайны
        # в pipeline сделаем пайплайн для сохранения данных class GbMongoPipeline:


        print(1)