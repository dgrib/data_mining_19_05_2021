import scrapy
from gb_parse.spiders.hh_spider.hh_xpath_selectors import VACANCY, VACANCY_DATA, PAGINATION, COMPANY_DATA
from .hh_loaders import HhVacancyLoader, HhCompanyLoader
from copy import copy
from urllib.parse import urlencode


class HhRemoteJobSpider(scrapy.Spider):
    name = 'hhremotejob'
    allowed_domains = ["hh.ru", "*.hh.ru"]
    start_urls = ["https://perm.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    api_vacancy_list_path = "/shards/employerview/vacancies"
    api_vacancy_list_params = {
        "page": 0,
        "currentEmployerId": None,  # сюда кидать автора вакансии
        "json": True,  # возвращает json
        "regionType": "OTHER",  # CURRENT и OTHER будет - перебрать
        "disableBrowserCache": True,
    }

    def _get_follow(self, response, selector_str, callback):
        for a_link in response.xpath(selector_str):
            yield response.follow(a_link, callback=callback)

    def parse(self, response):
        for item in (PAGINATION, VACANCY):
            yield from self._get_follow(response, item["selector"], getattr(self, item["callback"]))

    def vacancy_parse(self, response):
        loader = HhVacancyLoader(response=response)
        # убрали url, в классе HhVacancyLoader в инит перегружаем и добавляем url там
        for key, value in VACANCY_DATA.items():
            loader.add_xpath(field_name=key, **value)  # чтобы применять re в xpath_selectors,
            # инече можно loader.add_xpath(key, value), а можно было на входе лоатера через re пропускать строку
        data = loader.load_item()
        yield response.follow(data['author'], callback=self.company_parse)
        yield data

    def company_parse(self, response):
        loader = HhCompanyLoader(response=response)
        for key, value in COMPANY_DATA.items():
            loader.add_xpath(key, value)
        data = loader.load_item()
        employer_id = response.url.split('/')[-1]
        params = copy(self.api_vacancy_list_params)  # так как асинхроный код, если не копировать а изменить объект,
        # а его другой task попытается использовать
        params['currentEmployerId'] = employer_id
        yield response.follow(
            self.api_vacancy_list_path + '?' + urlencode(params),
            # page=0&currentEmployerId=1740&json=true&regionType=CURRENT&disableBrowserCache=true = urlencode(params)
            callback=self.api_vacancy_list_parse,
            cb_kwargs=params,  # они для callback api_vacancy_list_parse, чтобы менять page для пегинации
        )
        params['regionType'] = 'CURRENT'  # теперь ищем вакансии автора в своем регионе
        yield response.follow(
            self.api_vacancy_list_path + '?' + urlencode(params),
            # page=0&currentEmployerId=1740&json=true&regionType=CURRENT&disableBrowserCache=true = urlencode(params)
            callback=self.api_vacancy_list_parse,
            cb_kwargs=params,  # они для callback api_vacancy_list_parse, чтобы менять page для пегинации
        )
        params['regionType'] = 'OTHER'  # меняем вакансии автора на другие регионы
        yield data

    def api_vacancy_list_parse(self, response, **params):
        data = response.json()
        if data['@hasNextPage']:
            params['page'] += 1
            yield response.follow(
                self.api_vacancy_list_path + '?' + urlencode(params),
                callback=self.api_vacancy_list_parse,
                cb_kwargs=params,
            )
        for vacancy in data['vacancies']:
            # scrapy отфильтрует дублирующиеся url на компании на которые уже ходил
            yield response.follow(
                vacancy['links']['desktop'],
                callback=self.vacancy_parse,
            )
