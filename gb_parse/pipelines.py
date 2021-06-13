# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .settings import BOT_NAME
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request  # объект request олицетворяет подготовленный запрос,
# и экземпляр класса request возвращается в процесс когда мы делаем response.follow


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class GbMongoPipeline:

    def __init__(self):
        client = MongoClient()
        self.db = client[BOT_NAME]  # все - бд есть

    def process_item(self, item, spider):
        collection_name = f"{spider.name}_{item.get('item_type', '')}"
        self.db[collection_name].insert_one(item)
        return item


# напишем новый пайплайн для сохранения файлов
class GbImageDownloadPipeline(ImagesPipeline):
    # process_item есть у родителей, GbImageDownloadPipeline разделяет process_item на 2 процеруры,
    # на постановку и скачивание задач get_media_requests и продолжать item_completed
    # scrapy процесс получает от паука item - информацию, передает его по цепочке пайплайнов всегда в process_item
    # и передает туда item и паука который этот item родил
    # ImagesPipeline разбивают процедуру process_item (она остается) но условно внутри нее запускаются две вещи.
    # process_item берет item которй мы дали и пердает в get_media_requests, а в info пакуется информацуия -
    # сколько стоит в очереди , сколько скачано какоцй паук, сколькол ожидается на скачивание
    # когда порожденняая get_media_requests задача выполнена , а выполняются они в рамках process_item,
    # там хитрая процедура - заглянуть в исходники.
    # потом в item_completed пакуется  results (список результатов), item, info
    # когда из item_completed возвращаем item - это фактически выход process_item становится и прилетаем на след пайпл
    # - где сохраняем в БД

    def get_media_requests(self, item, info):
        # ставит задачи на скачивание и опрелитть пути, тоесть это дб генератор который вернет объекты scrapyRequest,
        # который и возвращется follow. Тут не будем использовать колбэки -
        # результаты будут возвращяться сюдаже и обрабатываться внутри нашего родителя.
        # if item.get('photos'):
        #     # тогда ставим задачи на скачиваение фото
        #     for url in item['photos']:
        #         yield Request(url)
        # вместо верхнего, позволило убрать ненужное условие
        for url in item.get('photos', []):
            # тут можно днлать перебор ключей, в зависимости от того какие поля нужно скачивать
            # можно тут сделать маппер который будет работать для разного вида контента
            yield Request(url)

    def item_completed(self, results, item, info):
        # будет принимать сам item и info (это вспомогательный объект -
        # там хранится паук краулер и тд, инфа о нашем item)
        # results это объекты результов поставленных задач нашего медиа
        # можно скрапи через сетинги настроить чтобы он делал превью изображений, водяные знаки наложил,
        # но чтобы он работал надо поставить библиотеку работы с изображдениями pip install pillow
        # в result[0] стоит булево True если удалось ли достучаться, смогли ли  начать качать изображение
        # потом словарь - url - откуда скачан,
        # path - куда сохранен файл - относительно директории указанной в IMAGES_STORE
        # (имя файла генерируется(чтобы избежать коллизий-имя типа 'full/d582f5b5ea2d450907715b8152ed0713a0c14b2f.jpg')
        # так как файлов с названием logo в инете может быть тьма
        # резервируется, скачиваем файл и заполняем его байтиками, а зачем ждать завершения ввсего скачивания -
        # у нас файлы могут быть по Гб весить) можем не ждать и отдать item на сохранение и уже чтото делать
        # checksum (md5, hash-summ)-для целостности проверки,уникальность-по чексумме можно искать дубликаты объектов,
        # для файла независимо от его имени хэш-сумма дб уникальной, допустим меняете имя а сумма будет одинаковая
        # о чексумме очень быстро искать дубликаты, она чаще всего в ОС вычислена
        # и можем понимать , что 10 одинаковых файлов скачалось на разных объявлениях - мошенники, перекупы.
        # статус - скачан. качается failed
        if results:  # это если прилетел item без фото, то не нужно сохранять этот ключ
            item['photos'] = [itm[1] for itm in results]
            # вместо ссылки на фото в item, стал словарь с сылкой на фото, путем, чексум и статус
        return item

        # item это словарь который прилетел из car_parse
                # def car_parse(self, response):
                #     loader = AutoyoulaLoader(response=response)
                #     loader.add_value("url", response.url)
                #     for key, value in CAR_DATA.items():
                #         loader.add_xpath(field_name=key, **value)
                #     yield loader.load_item()
        # item это один и тот же объект - его id в каждом пайплайн одинаковый, и мы его изменяем
        # item['photos'] = [itm[1] for itm in results] в item_completed
