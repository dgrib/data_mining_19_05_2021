import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instagram.insta_handshake import InstaHandshakeSpider

if __name__ == '__main__':
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("instagram.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(
        InstaHandshakeSpider,
        login=os.getenv("LOGIN"),
        password=os.getenv("PASSWORD"),
        # user_1=input(),
        user_1='dmgrib',
        # user_2=input(),
        user_2='timatiofficial',
    )
    crawler_process.start()
