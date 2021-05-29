import typing
import time
import requests
import bs4
from urllib.parse import urljoin
import pymongo
from datetime import datetime


class GdBlogParse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    _parse_time = 0

    def __init__(self, start_url, db, delay=1.0):
        self.start_url = start_url
        self.db = db
        self.delay = delay
        self.done_urls = set()
        self.tasks = []
        self.tasks_creator({self.start_url, }, self.parse_feed)

    def _get_response(self, url):
            next_time = self._parse_time + self.delay
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            print(f"RESPONSE: {response.url}")
            self._parse_time = time.time()

            if response.status_code == 200:
                return response

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            response = self._get_response(url)
            return callback(response)
        return task

    def tasks_creator(self, urls: set, callback: typing.Callable):
        urls_set = urls - self.done_urls
        for url in urls_set:
            self.tasks.append(
                self.get_task(url, callback)
            )
            self.done_urls.add(url)

    def run(self):
        while True:
            try:
                task = self.tasks.pop(0)
                task()
            except IndexError:
                break

    def parse_feed(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        ul_pagination = soup.find('ul', attrs={"class": "gb__pagination"})
        self.tasks_creator(
            set(
                urljoin(response.url, itm.attrs.get('href'))
                for itm in ul_pagination.find_all('a')
                if itm.attrs.get('href')
            ),
            self.parse_feed
        )

        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.tasks_creator(
            set(
                urljoin(response.url, itm.attrs.get('href'))
                for itm in post_wrapper.find_all("a", attrs={"class": "post-item__title"})
                if itm.attrs.get('href')
            ),
            self.parse_post
        )

    def parse_post(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        author_name_tag = soup.find('div', attrs={"itemprop": "author"})
        data = {
            'url': response.url,
            "title": soup.find('h1', attrs={'class': 'blogpost-title'}).text,
            "img": soup.find("div", attrs={"class": "blogpost-content"}).find(['img', 'iframe'])['src'],
            "date_published": datetime.fromisoformat(
                soup.find("div", attrs={"class": "blogpost-date-views"}).find('time')['datetime']
            ),
            "author": {
                'url': urljoin(response.url, author_name_tag.parent.attrs['href']),
                'name': author_name_tag.text
            }
        }
        self._save(data)



    """
        #    url страницы материала
        #    Заголовок материала
        #    Первое изображение материала (Ссылка)
        #    Дата публикации (в формате datetime)
        #    имя автора материала
        #    ссылка на страницу автора материала
        комментарии в виде (автор комментария и текст комментария)
    """

    def _save(self, data: dict):
        collection = self.db["gb_blog_parse"]
        collection.insert_one(data)
        print(1)


if __name__ == '__main__':
    client_db = pymongo.MongoClient()
    db = client_db['db_parse_19_05']
    parser = GdBlogParse('https://gb.ru/posts', db)
    parser.run()
