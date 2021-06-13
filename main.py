from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.hh_spider.hhremotejob import HhRemoteJobSpider
from gb_parse.spiders.youla_spider.autoyoula import AutoyoulaSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(AutoyoulaSpider)
    # crawler_process.crawl(HhRemoteJobSpider)
    # тут перед созданием процесса можно определить ссылки (хранить состояние пройденных ссылок)
    # можно созранить в БД set() ссылкок на которых уже были и в момент старта программы его подкидывать,
    # а в момент завершения программы - сохранять
    # если добавить в хранилище пройденных ссылок какието ссылки перед запуском - он по ним не пойдет.
    crawler_process.start()
