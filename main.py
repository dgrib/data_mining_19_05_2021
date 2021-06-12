from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.hh_spider.hhremotejob import HhRemoteJobSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    # crawler_process.crawl(AutoyoulaSpider)
    crawler_process.crawl(HhRemoteJobSpider)
    crawler_process.start()
