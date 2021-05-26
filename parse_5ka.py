import json
from pathlib import Path
import requests
import time

# url = 'https://5ka.ru/api/v2/special_offers/'
#
# # параметры и заголовки не всегда обязательны
# params = {
#     'store': '8471'
# }
# headers = {
#     'User-Agent': 'you can write what you want here' # на нашем сайте не влияет,
#     # то что мы сюда написали что угодно и данные отдает сайт, но может и влиять на получение данных
# }
# # response = requests.get(url, params=params, headers=headers)
# response = requests.get(url, headers=headers)  # убрали params=params - это убрали фильтрацию по конкретному магазу
#
#
# # tmp_file = Path('tmp.html')  # определили путь относительно проекта, но это не совсем правильно
# tmp_file = Path(__file__).parent.joinpath('tmp.html')
# # Path(__file__) - полный (мультиплатформенно) путь к файлу в котором эта переменная была вызвана
# # Path(__file__).parent - директолрию родителя этого пути
# # __name__ предоставляет имя импорта этого файла '__main__' если он был запущен
# # так путь формируется динамически - это правильно!!!!!!!!!!!
#
# # используя requests мы использыем его API и метод get как часть этого API,
# # который деклароирует нам определенное с ним взаимодействие -> (url, params=params, headers=headers)
# # итак все методы и тд
# # используя Path используем его API как parent метод, как joinpath метод
#
# #  и теперь надо записать контент из response в файл
# # писать будем не в текстовом а в байтовом виде чтобы не потерять контекст кодировок
#
# # перестанем писать в файл
# # tmp_file.write_bytes(response.content)  # делает тоже что и менеджер контекста with....
#
# # with open(tmp_file, 'wb') as file:
# #     file.write(response.content)
#
# data = response.json()
#
# print(1)


class Parse_5ka:
    headers = {
        'User-Agent': 'loh'  # на нашем сайте не влияет,
        # то что мы сюда написали что угодно и данные отдает сайт, но может и влиять на получение данных
    }

    def __init__(self, start_url, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path  # буду передавать путь к директории, в которую я хочу сохранять product

    def _get_response(self, url):
        """Выделен отдельно, так как могут случаться ошибки - сервер может ответить не с 200 кодом
        он протектный - не публичный метод - извне пользовааться не нужно,
        Просто из экземпляра обращаться к методу _get_response не нужно"""
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:  # использовать status_code лучше так как предоставляют они int данные
                                             # и как минимум это меньше весит, а response.OK сравнение со строкой, нафига
                                             # если можно сравнивать числа, это быстрее
                return response
            time.sleep(0.5)  # нехорошо повторять запрос сразу,
                             # если не отдали запрос кодом 200, значит чтото пошло не так - надо немного поспать

    def run(self):
        """Только это публичный метод, все остальные должны испольтзоваться либо внутри модуля,
        либо внутри класса (если внутри этого класса убдет еще класс, который бедт взаимодействовать с этими методами),
         либо не использоваться вовсе."""
        for product in self._parse(self.start_url):  # product ожидаем словарь,
                                                     # то их мы будем сохранять, надо для начала сделать имя файла
            file_path = self.save_path.joinpath(f"{product['id']}.json")  # формируем имя файла уникальное
            self._save(product, file_path)

    def _parse(self, url):
        """Будет принимать url, должен запросить response по этому url, определить пеггинацию,
         разобрать попродуктно, поэтому он будет генератором -
         он будет отправлять назад, изменять свой url и идти дальше по пегинации,
         так как в некст хранится Url на следующую страницу"""
        while url:
            response = self._get_response(url)  # если response вернлся в данном методе, значит там json
            data: dict = response.json()
            url = data['next']  # изменяем url
            for product in data['results']:
                yield product

    def _save(self, data: dict, file_path: Path):
        """В метод save убдем присылать данные в виде словаря и файлпуть"""
        file_path.write_text(json.dumps(data, ensure_ascii=False))  # ensure_ascii=False
        # чтобы русские симвлы выглядели в файле нормально,
        # по дефолту json.dumps преобразщует все символы к ascii символам,
        # и русскочзычные имена строки могут не читатсья человеком, если их обратно слоадить, то все будет холрошо
        # ensure_ascii=False - если хотим сохранить читабельность


def get_save_path(dir_name: str) -> Path:
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():  # проверяет существование директории
        save_path.mkdir()
    return save_path


if __name__ == '__main__':
    url = 'https://5ka.ru/api/v2/special_offers/'
    product_path = get_save_path('products')
    parser = Parse_5ka(url, product_path)
    parser.run()

