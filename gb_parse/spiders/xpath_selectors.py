BRANDS = {
    "selector": "//div[contains(@class, 'Filters_brandsList')]"
                "//a[@data-target='brand']/@href",
    "callback": "brand_parse",
}
PAGINATION = {
    "selector": "//div[contains(@class, 'Paginator_block__2XAPy')]"
                "//a[@data-target-id='button-link-serp-paginator']//@href",  # тут не ссылка а ссылки
    "callback": "brand_parse",
}

CARS = {
    "selector": "//article[@data-target='serp-snippet']"
                "//a[@data-target='serp-snippet-title']//@href",
    "callback": "car_parse",
}

# CAR_DATA = {
#     "title": "//div[@data-target='advert-title']/text()",
#     "photos": "//img[contains(@class, 'PhotoGallery_photo')]/@src",
#     "characteristics": "//div[contains(@class, 'AdvertCard_specs')]"
#                        "/div/div[contains(@class, 'AdvertSpecs_row')]",
#     # характеристики являются списком строк селекторов, делаем from scrapy import Selector
#     "price": "//div[@data-target='advert-price']/text()",
#     "descriptions": "//div[@data-target='advert-info-descriptionFull']/text()",
#     "author": "//script[contains(text(), 'window.transitState = decodeURIComponent')]",
#     # в терминале имея loader вводим
#     # re_pattern = r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar"
#     # loader.add_xpath("tmp", "//script[contains(text(), 'window.transitState = decodeURIComponent')]", re=re_pattern)
#     # создаем ключ новый "tmp", дальше строка xpath строка селектора,
#     # говорим: лоадер примени к данному объекту регулярное выражение
#     # a = loader.load_item()
#     # Но чтобы получить такой интерфейс надо поименять xpath селекторы
#     будем передавать loader.add_xpath(field_name=key, **value) !!!! field_name=author ** xpath= re=
# }

CAR_DATA = {
    "title": {"xpath": "//div[@data-target='advert-title']/text()"},
    "photos": {"xpath": "//img[contains(@class, 'PhotoGallery_photo')]/@src"},
    "characteristics": {"xpath": "//div[contains(@class, 'AdvertCard_specs')]"
                                 "/div/div[contains(@class, 'AdvertSpecs_row')]"},
    "price": {"xpath": "//div[@data-target='advert-price']/text()"},
    "descriptions": {"xpath": "//div[@data-target='advert-info-descriptionFull']/text()"},
    "author": {"xpath": "//script[contains(text(), 'window.transitState = decodeURIComponent')]",
               "re": r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar"
               },
    # номер телефона - поисследовать данные - он в той же структуре данных что и id пользователя
}
