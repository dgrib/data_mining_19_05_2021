import typing
import time
import requests
from urllib.parse import urljoin
import bs4
import pymongo
from database.database import Database  # импортировали класс для взаимодействия с БД


class GbBlogParse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) "
                      "Gecko/20100101 Firefox/88.0"
    }
    __parse_time = 0

    def __init__(self, start_url, db:Database, delay=1.0):  # db:Database измениили
        self.start_url = start_url
        self.db = db
        self.delay = delay
        self.done_urls = set()
        self.tasks = []
        self.tasks_creator({self.start_url, }, self.parse_feed)

    def _get_response(self, url):
        while True:
            next_time = self.__parse_time + self.delay
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            print(f"RESPONSE: {response.url}")
            self.__parse_time = time.time()
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
        pagination_links = set(
            urljoin(response.url, itm.attrs.get('href'))
            for itm in ul_pagination.find_all('a') if
            itm.attrs.get("href")
        )
        self.tasks_creator(pagination_links, self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.tasks_creator(
            set(
                urljoin(response.url, itm.attrs.get('href'))
                for itm in post_wrapper.find_all("a", attrs={"class": "post-item__title"}) if
                itm.attrs.get("href")
            ),
            self.parse_post
        )

    def parse_post(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        author_name_tag = soup.find('div', attrs={"itemprop": "author"})
        data = {
            "post_data": {
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "url": response.url,
                "id": int(soup.find("comments").attrs.get("commentable-id")),
            },
            "author_data": {
                "url": urljoin(response.url, author_name_tag.parent.attrs.get("href")),
                "name": author_name_tag.text,
            },
            "tags_data": [
                {"name": tag.text, "url": urljoin(response.url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comments(soup.find("comments").attrs.get("commentable-id")),
        }
        self._save(data)

    def _save(self, data: dict):
        self.db.add_post(data)  # сделали для sqlalchemy
        # collection = self.db["gb_blog_parse"] это было нужно для mongo
        # collection.insert_one(data)

    def _get_comments(self, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = self._get_response(urljoin(self.start_url, api_path))
        data = response.json()
        return data


if __name__ == '__main__':
    client_db = pymongo.MongoClient("mongodb://localhost:27017")
    orm_database = Database('sqlite:///gb_blog_parse.db')
    # в качестве юрл будем использовать строку соединения с sqlite
    # /gb_blog_parse.db - это относительный путь к файлу, так как sqlite это файловая бд ,
    # вместо него писать полный путь если нужно
    # sqlite: // - это схема к чему соединяемся
    # db = client_db["gb_parse_18_05"] было для монго
    # parser = GbBlogParse("https://gb.ru/posts", db) было для монго
    parser = GbBlogParse("https://gb.ru/posts", orm_database)
    parser.run()

# в консоли collection = db["gb_blog_parse"], потом a = collection.find() по а потом можно итерироваться
# коллекция это итерируемый обхъект и у него схожая модель поведения с итераторрами
# курсор перемещается по базе (а) вынимая поледующий объект
#for itm in collection.find({"comments_data": []}):
#     print(itm)+
# for itm in collection.find({"title": {"$regex": "Бизнес"}}):
# выдпаст где в title есть слово Бизнес, регистр учитывается, если в начале строки {"$regex": "^Бизнес"}
# можно задать количество выборки указав count, можно делать реплейсы данных
# for itm in collection.find({"url": {"$in": [список url-ов]}}):
# выведет все записи чей url был в списке
# можно regex совмещать с in, использовать and not nor, type (когда значение поля имеет определенный тип)
# gte lte
# for itm in collection.find({'comments_data': {"$size": 2}}):  размер списка равен 2
# for itm in collection.find({'comments_data': {"$gt": {"$size": 2}}}): больше 2
# если правильно настроенные sql можно добиться большей производительности чем стандартный nosql, но это искусство
# ORM 1- безопасно, так как если писать на чистом sql запросы то инъекции мб
#       2- последовательность колонок надо помнить, когда sql отдает в видле массива где последовательно идут поля
#       3- python ооп язык ,все есть объект, то удобно иметь описание бд в виде классов,
#       где каждая таблица описана в виде класса, а экземпляр является для нас олицетворением записи
#  А пистаь на двух языках это путь к раздвоению личности
# pip install sqlalchemy используют на крупнейших проектах в мире, но Она не единственная библиотека,
# есть много реализаций ORM, например в jango свой
# в качестве бд будем испольовать sqlite, Но alchemy поддерживает много бд, и написанный ORM на уроке,
# просто поменяв строку коннекта не к sqlite, а указав postgre - сможете работать с ней, прямо напрямую.
# Без изменения кода. Можно отладиться на sqlite а потом работать с postgres не изменяя код.
# создаем папку python package, там делаем models, под моделью понимается класс, нгаписанныс с использованием ORM ,
# который олицетворяет Таблицу. Совокупность моделей олицетворяет базу. Таблица это совокупность определенных колонок.

