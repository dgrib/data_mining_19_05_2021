from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .avito_xpath_selectors import ADVT_DATA
from .avito_prosessors import avito_user_url, to_float, clean_parameters, flat_text


class AvitoRealEstateLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    item_type_out = TakeFirst()
    title_out = TakeFirst()
    price_out = TakeFirst()
    price_in = MapCompose(to_float)
    address_in = MapCompose(flat_text)
    address_out = TakeFirst()
    user_link_in = MapCompose(avito_user_url)
    user_link_out = TakeFirst()
    parameters_in = MapCompose(clean_parameters)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("response"):
            self.add_value("url", self.context["response"].url)
        self.add_value('item_type', 'real_estate')
        for key, value in ADVT_DATA.items():
            self.add_xpath(key, **value)

