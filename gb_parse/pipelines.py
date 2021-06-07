# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .settings import BOT_NAME
from pymongo import MongoClient


class GbParsePipeline:
    def process_item(self, item, spider):
        return item
        # этот return отправляет данные обратно в процесс а процесс отправляет данные в следующтий пл по приоритету


class GbMongoPipeline:  # scrapy требует соблюдапть определенного интерфейс

    def __init__(self):  # инициализируем БД так как хотим с ней работать
        client = MongoClient()
        self.db = client[BOT_NAME]  # все - бд есть

    def process_item(self, item, spider):  # метод должен быть у любого pipeline
        self.db[spider.name].insert_one(item)  # у нас есть объект паука,
        # от которого нам пришел item, значит есть его name
        return item  # важно для всей пайплайнов

# как пайплайны работают (трубопровод)
# пайплаынй собираются в цепочку, укажем их в настройках, первый пл принимет значение и паука от которого это перешло,
# чтотоделает с этими данными и возвращает item - то чтоон возвращает - передается на вход следующему и тд.