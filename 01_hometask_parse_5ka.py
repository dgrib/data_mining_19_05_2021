import json
import time
from pathlib import Path
import requests


class Parse5ka:
    headers = {
        "User-Agent": "Philip Kirkorov"
    }
    params = {
        "store": "8471",  # скачиваем в определенном магазине, чтобы не так долго было
    }

    def __init__(self, start_url, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, params=self.params, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        response_cat = self._get_response(url_cat)
        data_cat = response_cat.json()

        for cat in data_cat:
            final_dict = {}  # структура для заполнения в каждый файл
            product_list = []  # обновляется для каждой категории
            group_code = cat['parent_group_code']  # Код соответствующей категории (используется в запросах)
            group_name = cat['parent_group_name']  # Имя категории для имени файла

            self.params['categories'] = group_code  # меняем Код категории в параметрах запроса

            for product in self._parse(self.start_url):
                product_list.append(product)

            # заполняем словарь перед сохранением в файл
            final_dict["name"] = group_name
            final_dict["code"] = group_code
            final_dict["products"] = product_list

            file_path = self.save_path.joinpath(f"{group_name}.json")
            self._save(final_dict, file_path)

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data["next"]

            for product in data['results']:
                yield product

    def _save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False))


def get_save_path(dir_name: str) -> Path:
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == '__main__':
    url = "https://5ka.ru/api/v2/special_offers/"
    url_cat = "https://5ka.ru/api/v2/categories/"
    product_path = get_save_path('products')
    parser = Parse5ka(url, product_path)
    parser.run()
