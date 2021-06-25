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
        self.db = client[BOT_NAME]

    def process_item(self, item, spider):
        collection_name = f"{spider.name}_{item.get('item_type', '')}"
        self.db[collection_name].insert_one(item)
        return item


class GbImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for candidate in item['data']['image_versions2'].get('candidates', []):
            url = candidate['url']
            yield Request(url)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results]
        return item
