ADVT = {
    "selector": "//div[contains(@class, 'iva-item-titleStep')]/a/@href",
    "callback": "advt_parse",
}

ADVT_DATA = {
    'title': {'xpath': "//h1[@class='title-info-title']/span/text()"},
    'price': {'xpath': "//span[@itemprop='price']/@content"},
    'address': {'xpath': "//div[@class='item-address']//span[@class='item-address__string']/text()"},
    'parameters': {'xpath': "//ul[@class='item-params-list']/li"},
    'user_link': {'xpath': "//div[@class='seller-info-value']//a/@href"},
}

# Дополнительно но не обязательно вытащить телефон автора