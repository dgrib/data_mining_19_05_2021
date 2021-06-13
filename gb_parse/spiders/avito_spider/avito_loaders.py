from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from gb_parse.spiders.hh_spider.hh_prosessors import flat_text, hh_user_url, hh_sphere_activities_clean, concatenate_items


class HhVacancyLoader(ItemLoader):
    default_item_class = dict
    item_type_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = flat_text
    description_out = flat_text
    author_in = MapCompose(hh_user_url)
    author_out = TakeFirst()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("response"):
            self.add_value("url", self.context["response"].url)
        self.add_value("item_type", "vacancy")
