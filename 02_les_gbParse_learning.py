# есл ирекурсивно идти по пегинации, то на большом ресукрсе будет переполнение.
# каждый переход на страницу и обработка - это одна задача. Всего 2 вида задач, пегинация и обработка каждой статьи
# задачи будем храниитьт в очереди fifo
# цикл будет идти по итерированному объекту ,брать оттуда задачу, выполнять ее и переходитьт к следующей.
# выполняемая задача может пополнить этот список (объект) новыми задачами

import typing
import time
import requests
import bs4
from urllib.parse import urljoin  # крутой умный конкатинатор url
# urljoin('https://gb.ru/posts', '/posts?page=2')  -> 'https://gb.ru/posts?page=2'
# urljoin('https://gb.ru/posts', 'https://gb.ru/posts?page=2')  -> 'https://gb.ru/posts?page=2'


class GdBlogParse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    _parse_time = 0 # выгодно - мало весит

    def __init__(self, start_url, delay=1.0):
        self.start_url = start_url
        self.delay = delay
        self.done_urls = set()  # будем сохранять url куда уже ходили, свойства set - уникальные элементы,
        # работает быстрее - более оптимизированно хранятся даннеые внутри, хеши, поиск быстрый, есть такое значение
        # или нет  (tuple - не добавтиь новое занчение, )
        self.tasks = []  # нужна очередь задачь,
        # в питоне конечно есть очереди и они позволяют быстро делать fifo or filo, но мы сделаем упрощенно на списке,
        # это неправильно в продашне, но в целом можно и так
        self.tasks_creator({self.start_url, }, self.parse_feed)  # создаем первую задачу, даем set url-ов и ф-ю обработки

    def _get_response(self, url):  # хочу чтобы глобально не делались запросы чаще определенного времени,
                # чаще чем это делается через delay,
                # для этого вводим приватный атрибут _parse_time
        # next_time = self._parse_time + self.delay   ===== перенесли вниз, атк как будет проблема времени
        while True:  # реализуем сон между запросами
            next_time = self._parse_time + self.delay
            if next_time > time.time():  # выгодно time.time() = float
                time.sleep(next_time - time.time())  # ексли будем делать _get_response когда вроемя еще не пришло,
                                    # то наш парсер уснет на время нужное, потом проснется и сделает запрос.
                # надо всегда учитывать время когда можно сделать запрос
                # сделав запрос - мы запоминаем время когда мы его сделали, и каждый раз будем сверяться с этим внеменем,
                # вначале parse_time = 0 и значит время пришло всегда.
                # next_time не будет больше time.time (время от 1970 года в секундах)
                # если мы слишкоим быстро сделаем запрос, тоесть next_time > time.time() - то условие if нас сдержит
                # и уснет на разницу next_time - time.time()
            response = requests.get(url, headers=self.headers)
            print(f"RESPONSE: {response.url}")
            self._parse_time = time.time()  # фиксируем _parse_time после запроса, для задержки потом в if
    # респонз может обрабатываться и 5-10 секунд.Если просто задержку поставить то будет всегда задержка,
            # а с подсчетом как тут, более эффективно расходуется время, так как пауза будет только в том случае,
            # если запрособрабатывалося меньше delay

            if response.status_code == 200:  # статус код выгоден так как с числом сравниваем
                return response

    # методика замыкания, похож на декораторы
    # это же можно организовать с помощью снешних классов,
    # определить определенный колабл класс и использовать его в виде задач
    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable: # передаем url и  ф-ю которая должна яего обработать
        # хотим обрабатывать без рекурсий, имеем обэект обработчик, и откладываем задачи на потом
        def task():  # ничего не принимает но делает важную вещь,
            response = self._get_response(url)  # тут мы должны получить некий респонз и передать его в колбэк
            return callback(response)  # ретерним колбэк и выполняем его, передав туда респонз
        return task
    # когда указываешь тип url например, ide подсказывает - чего оти меня ожидает ф-я,
    # плюс линтеры могут показывать потенциальные ошибки в вашем коде, безопасность кода так лучше обеспечивается
    # СТРОГАЯ ТИПИЗАЦИЯ если будете контролировать каждый тип и знать где что происходит, лучше чем динамич.
    # динамич только изза того что она есть используете?

    def tasks_creator(self, urls: set, callback: typing.Callable):  # ничего не возвращаем
        # нужно вычислить те url которые обработаны и удалить из списка url и после этого насоздавать задач
        urls_set = urls - self.done_urls  # вычитаем мноджества, оставляем urls которые не входят в done_urls
        for url in urls_set:
            self.tasks.append(
                self.get_task(url, callback)
            )
            self.done_urls.add(url)  # добавляем в сделано, так как задачу создали по этому url



    def run(self):  # будет просто запускать цикл
        # # как ссылки извоекать? создадим первую задачу - это можно сджелать в разных местах (в ините можно, тут можно)
        # self.tasks.append(self.get_task(self.start_url, self.parse_feed))  # старт url будет обрабатываться feed
        # # результат работы get_task это ф-я task !!!!!!
        # # для определенной task существует в ее области видимости url и метод (в даннном случае parse_feed)
        # self.done_urls.add(self.start_url)  # если задача поставлена - url утилизирован
        # потом вынесли верхнее в инит, но в tasks_creator - и run стыл чистый

        while True:
            try:
                task = self.tasks.pop(0)  # извлекаем из очережи задачу под 0 индексом,
                # так как она колабл мы ее вызываем ниже
                task()  # и он будет работать, вызывыаем его на обработку задачи,
                # при ее вызове мы попаданем в def task, для него существует определенный url и опред callback
                # на этот url мы делаем запрос, получаем запрос и передаем его в колбэк,
                # которым является parse_feed (в данном случае), а он должен извлечь ссылки и породить новые таски аппендить
            except IndexError:  # исключение мб только если список задач пустой
                break
            # отлавливать исключение выгоднее, чем постоянно мерить длину списка
            # у нас есть ошибка которую мы ждем, это быстрее, знаем как на нее отреагировать, не надо if-else
            # сложность алгоритма проще

    # теперь нудны всего 2 обработчика задач, обрабатывать страницы со списком постов, и пегинацией
    # страница ленты и страница самого поста - это два разных обработчика, если делать единым обработчиком
    # - это будут сложные условия
    # dry - don't repeat yourself, solid - заставляет нас декомпозировать задачу
    # вот есть задача обрабатывать запросы с учетом времени get_response
    # есть задача пораждать таски - у нас етсь метод get_task
    # можно было в один? да, но плдохо было бы
    def parse_feed(self, response: requests.Response,  ):  # собирает из респонза все ссылки на пегинацию и посты,
                                                            # пораждать задачи, будет пополнять tasks (в виде колбл объектов)
        soup = bs4.BeautifulSoup(response.text, 'lxml')  # по умолчанию html.parse
        # BS не умеет делать запросы, не умеет работать с хедерами, может обрабатывать только текстовую информацию
        # ему надо передавать html или xml в виде текстовой строки
        # можно скачаать весь сайт ссылки html а потом его обработать c помощбю BS
        ul_pagination = soup.find('ul', attrs={"class": "gb__pagination"})
        pagination_links = set(
            urljoin(response.url, itm.attrs.get('href')) for itm in ul_pagination.find_all('a') if itm.attrs.get('href')
        )
        # itm.attrs.get('href') for itm in ul_pagination.find_all('a') if itm.attrs.get('href') - было так
        # {'/posts?page=2', '/posts?page=3', '/posts?page=57'} а стали полные ссылки

        # щас нам нужно породить задачу, у нас относительбные url в pagination_links
        self.tasks_creator(pagination_links, self.parse_feed)
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        post_links = set(
            urljoin(response.url, itm.attrs.get('href'))
            for itm in post_wrapper.find_all("a", attrs={"class": "post-item__title"})
            if itm.attrs.get('href')
        )
        self.tasks_creator(post_links, self.parse_post)

        # можно так заменить верхнее, post_links убрать, но такой код сложне некоторым читать
        # self.tasks_creator(
        #     set(
        #         urljoin(response.url, itm.attrs.get('href'))
        #         for itm in post_wrapper.find_all("a", attrs={"class": "post-item__title"})
        #         if itm.attrs.get('href')
        #     ),
        #     self.parse_post
        # )

    def parse_post(self, response: requests.Response):  # долджен обрадатывать страницу поста и извлекать из него данные
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        author_name_tag = soup.find('div', attrs={"itemprop": "author"})
        data = {
            'url': response.url,
            "title": soup.find('h1', attrs={'class': 'blogpost-title'}).text,  # делали в консоли, из soup... при дебаге
            # хотим имя автора и ссылку на автора
            "author": {
                'url': urljoin(response.url, author_name_tag.parent.attrs['href']),
                'name': author_name_tag.text
            }
            # обработку более сложных структур можно вынести в отдельные методы
        }
        self._save(data)

    def _save(self, data: dict):
        print(1)


if __name__ == '__main__':
    parser = GdBlogParse('https://gb.ru/posts')
    parser.run()

# инсталлируем монго на комп