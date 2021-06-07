# это упрощает сложности css selectors
# Объекты скрапи именуются с разлимчныфми суффиксами, методы обрабатывающтие страницы ..._parse например
# пауки ...Spider
# лоадеры изначально принимают re и оно будет обработано
# пишем мало кода, в основном донастраиваем классы и объекты фреймворка,
# чтобы они  поняли какой результат мы от них ожтдаем
from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


def clear_price(price: str) -> float:  # очищает price от ненужных utf символов
    try:
        result = float(price.replace("\u2009", ""))
    except ValueError:
        result = None
    return result

# написал процедру- вынес ее из паука - сюда в лоадер
def get_characteristics(item: str):  # один из селекторов допустим для года авто или пробега приходит сюда
    selector = Selector(text=item)
    data = {
        "name": selector.xpath("//div[contains(@class, 'AdvertSpecs_label')]/text()").get(),
        "value": selector.xpath("//div[contains(@class, 'AdvertSpecs_data')]//text()").get(),
        # value извлекли из любой вложенности (там были данеы в ссылке а внутри div, вместо просто в div) !!!!
    }
    return data


# def take_first(items):  # простейштй постпроцессор, заменили на стандартный TakeFirst
#     return items[0]

def create_author_link(author_id: str) -> str:
    author = ''
    if author_id:  # моет прийти None и будет проблема поэтому проверяем существование
        author = urljoin('https://youla.ru/user/', author_id)
    return author


class AutoyoulaLoader(ItemLoader):  # loader это такой класс
    # который через спец интерфейс будет принимать в себя response потом принимает в себя query xpass or css
    # и занимается всей обработкой для данного поля,
    # "мне нужно чтобы в конечном айтеме было такое поле, а значение положить из этого селектора"
    # назначение лоадера подготовить конечную структуру для сохранения, тоетсь паук не занимаетсчя обработкой респонза
    # конечную структуру будет собирать лоадер
    default_item_class = dict
    # есть препроцессоры и построцессоры. in обработка до складирования данных в атрибут url например,
    # данные получены обработаны а потом положены в хранилище
    # out это когда мы говорим load_item(), тоесть когда они возвращаются нам из хранилища
    # dict создается класс и заполняется тем что лежит в _value loader
    # url_out = take_first  # тут надо указывать именно колабл объекты, класс или экз класса - но колабл объект
    url_out = TakeFirst()  # тут вызов() делаем так как это класс у которого перегружен метод __call__
    title_out = TakeFirst()
    # photo никак не надо - лежат в списке ссылок
    price_in = MapCompose(clear_price)  # указываем функцию очистки. MapCompose это тоже колабл объект,
    # но в отличие от map, он может на вход принять цепочку колабл объектов обработчиков.
    # И он сам колабл - он принимает итерируемый объект - берет оттуда как обычный map элемент -
    # прогоняет сначала через первую переданную ф-ю, потом через вторую и тд. И результат возвращает в конечном списке.
    price_out = TakeFirst()
    description_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)
    author_in = MapCompose(create_author_link)  # функция переводит id автора в url
    author_out = TakeFirst()


