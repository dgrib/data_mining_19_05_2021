from scrapy import Selector
from urllib.parse import urljoin


def clean_parameters(item):
    selector = Selector(text=item)
    data = {
        "name": selector.xpath("//span[@class='item-params-label']/text()").extract_first(),
        "value": selector.xpath("//a[contains(@class, 'item-params-link')]/text()").get(),
    }
    if not data["value"]:  # когда значение не ссылка на ЖК, а просто текст в li
        value_result = ""
        for item in selector.xpath("//li/text()").extract():
            if item and not item.isspace():
                value_result += item
        data["value"] = value_result
    return data


def avito_user_url(user_id):
    return urljoin("https://avito.ru/", user_id)


def to_float(item):
    try:
        data = float(item)
    except ValueError:
        data = None
    return data


def flat_text(items):
    return items.strip()


# def to_type(type_cls):  # можно передать тип не вызвав ф-ю, разобраться
#     def procedure(item):
#         try:
#             data = type_cls(item)
#         except ValueError:
#             data = None
#         return data
#
#     return procedure