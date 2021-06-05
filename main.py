# через него будем запускать и отлаживаться
# в рамках одного проекта может рабогтать несколько пауков, ктото должен ими управлять,
# для этого есть класс управляющегно процесса, через него запускаются все остальные пауки
from scrapy.crawler import CrawlerProcess  # мы только запускаем процессс а он сам рулит пауками запросами настройками
from scrapy.settings import Settings  # чтобы корректно импортровать все настройки

from gb_parse.spiders.autoyoula import AutoyoulaSpider  # импортируем нашего паука

if __name__ == '__main__':
    crawler_settings = Settings()  # инициализируем класс Settings
    crawler_settings.setmodule("gb_parse.settings")  # наш экз класса settings считает файл и правильно настроится
    crawler_process = CrawlerProcess(settings=crawler_settings)  # создаем процесс,
    # теперь процесс подготовлен чтобы начать работу, но он ничего не знает еще о наших пауках
    crawler_process.crawl(AutoyoulaSpider)  # добавляем паука в процесс, добавляем класс!!! не экземпляр
    # crawler_process.crawl(AutoyoulaSpider) # может быть несколько разнеых паукаов, а старт один,
    # один же процесс для всех пауков. Сам экз класса будет создавать наш процесс
    crawler_process.start()
