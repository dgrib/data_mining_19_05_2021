import scrapy


class AutoyoulaSpider(scrapy.Spider):  # это паук
    name = 'autoyoula'  # имя паука, нужно для управления когда много пауков
    allowed_domains = ['auto.youla.ru']  # список доменов куда разрешено ходить нашему пауку,
    # так как, когда заберет все ссылки, чтобы не пошел по инету, переходя по ссылкам - scrapy ему не позволит
    start_urls = ['https://auto.youla.ru/']  # по дефолту http адреса,
    # добавляем s и экономим один запрос - хотя и так будет работать
    # мы не запускали паукуа - его запустил процесс,
    # процесс смотрт на этот список - делает асинхронно запросы на них, условно-параллельно друг другу,
    # по мере ответов - формирует объект респонз в метод parse паука.
    # Сеачала от первого url response, потом от второго - асинхронно - в порядке очереди

    # def parse(self, response):  # Должен быть всегда иначе проблемы
        # # response не только инфу содежит как request.response но и структуру html кода
        # # все что у request-овского response.url response.headers response.text
        # # но у него есть доп методы позволяющие извлекать данные - по css например парсинг (проще чем bs4)
        # # тут bs4 не нужен, response уже имеет все для доступа к данным. bs4 сюда тащить нет смысла
        # # a= response.css(".TransportMainFilters_brandsList__2tIkv a.blackLink") передаем css селектор
        # # a  - это SelectorList состоит из селекторов,  a[0] можно ...
        # # a[0].extract() извлекаем - получаем всю строку тега, а нам нужны данные из href атрибута
        # # a[0].attrib.get("href") - получили ссылку - и для последу.щих запросов,
        # # переходов нам нет необходимоси склеивать url, так как мы будем через объект response порождать задачи,
        # # мы не делаем запросы, мы порождаем задачи и возвращаем их управляющему процессу, он эти задачи выполняет
        # # мы пораждаем задачи через response а он содержит в себе url, и когда убдем передавать ему относительный url -
        # # он конкатенацуию url сделает правильно счамостоятельно
        # # response.urljoin('/yaroslavl/cars/used/ac/') у него есть метод urljoin, а в response уже етсь url - выдаст =>
        # # 'https://auto.youla.ru/yaroslavl/cars/used/ac/' - конкатинирует правиллньо
        # for a_link in response.css(".TransportMainFilters_brandsList__2tIkv a.blackLink"):
        #     url = a_link.attrib.get("href")
        #     # теперь надо породить задачу перехода на след страницу и передать туда ссылку
        #     yield response.follow(url, callback=self.brand_parse) # yield вернет значение тому кто запустил метод parse
        #     # от response следуй (follow) по url - и передать метод который будет обрабатывать response этого url
        #     # в callback мы уже переходим на страницу бренда
        # # метод parse только извлекает ссылки ,
        # # так как в орбработку данной страницы входит только извлечь ссылкии на бренды авто и породить задачи на переход
        # # и выкинутиь задачи обратно в управляющий процесс

    # def brand_parse(self, response):
        # # сюда уже приходит response со страницы бренда response.url = 'https://auto.youla.ru/yaroslavl/cars/used/ac/'
        #
        # # 2021-06-05 17:58:27 [scrapy.dupefilters] DEBUG: Filtered duplicate request:
        # # <GET https://auto.youla.ru/yaroslavl/cars/used/audi/> -
        # # no more duplicates will be shown (see DUPEFILTER_DEBUG to show all duplicates)
        # # scrapy ведет себя по дефолту так, если пытаетесь сделать запрос на url на который он уже сделал запрос ,
        # # то он это будет отфильтровывать и игнорировать - об этом беспокоиться не надо -
        # # то что мы хранили пройденное!!!! ссылки, scrapy делает сам из коробки
        #
        # # тут надо пройтись  по пегинации и породить задачки
        # for a_link in response.css('.Paginator_block__2XAPy a.Paginator_button__u1e7D'):  # проход по пегинации
        #     url = a_link.attrib.get("href")
        #     yield response.follow(url, callback=self.brand_parse)  # сам себя вызывает и проходит пегинацию

    def _get_follow(self, response, selector_str, callback): # чтобы убрать дублирование кода методов parse, brand_parse
        for a_link in response.css(selector_str):
            url = a_link.attrib.get("href")
            yield response.follow(url, callback=callback)

    def parse(self, response):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv a.blackLink",
            self.brand_parse
        )

    def brand_parse(self, response):
        yield from self._get_follow(  # тут мы говорим что не этот yield использовать, а втот что в методе _get_follow
            response,
            '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
            self.brand_parse
        )
        yield from self._get_follow(  # from значит используй yield из генератора self._get_follow
            response,
            "a.SerpSnippet_name__3F7Yu.blackLink",  # класс с подклассом blackLink 04_parsing 2-06
            self.car_parse
        )

    def car_parse(self, response):  # обрабатывает ссылки на страницы авто

        print(1)

    # сначала scrapy извлек все ссылки на бренды с главной страницы, перешгел по ним, на них он нашел ссылки пегинации,
    # (поставил задачи перехода по ним) перешел по ним, потом нашел все ссылки на объявления на этих страницах.
    # И поставил задачу перехода по ним.
    # scrapy тяжеловат для блога гикбрейнс например. А bs4 для 5ки не подойдет.
    # даже на ГБ bs4 бы не делал так как там все руками просто вытащить
    # bs4 часто используется и на сорбесах его требуют некоторые компании , задачи по нему дают, он простой,
    # в промышленных хадачах bs4 редко встречается, особенно после появления scrapy
    # bs4 хорош в задачах где scrapy не применить никак - например архив html документов или ftp с html документами
    # тут если scrapy то придется писать костыль чтобы пропихивать в скрапи вместо запросов файлы.
    # bs4 еще xml докумегнты обрабатывает
    # IT живет на англ языке, это данность профессии. Не хорошо и не плохо - это как гравитация, просто есть.


