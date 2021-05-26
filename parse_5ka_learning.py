import json
from pathlib import Path
import requests

url = 'https://5ka.ru/api/v2/special_offers/'

# параметры и заголовки не всегда обязательны
params = {
    'store': '8471'
}
headers = {
    'User-Agent': 'you can write what you want here' # на нашем сайте не влияет,
    # то что мы сюда написали что угодно и данные отдает сайт, но может и влиять на получение данных
}
# response = requests.get(url, params=params, headers=headers)
response = requests.get(url, headers=headers)  # убрали params=params - это убрали фильтрацию по конкретному магазу


# tmp_file = Path('tmp.html')  # определили путь относительно проекта, но это не совсем правильно
tmp_file = Path(__file__).parent.joinpath('tmp.html')
# Path(__file__) - полный (мультиплатформенно) путь к файлу в котором эта переменная была вызвана
# Path(__file__).parent - директолрию родителя этого пути
# __name__ предоставляет имя импорта этого файла '__main__' если он был запущен
# так путь формируется динамически - это правильно!!!!!!!!!!!

# используя requests мы использыем его API и метод get как часть этого API,
# который деклароирует нам определенное с ним взаимодействие -> (url, params=params, headers=headers)
# итак все методы и тд
# используя Path используем его API как parent метод, как joinpath метод

#  и теперь надо записать контент из response в файл
# писать будем не в текстовом а в байтовом виде чтобы не потерять контекст кодировок

# перестанем писать в файл
# tmp_file.write_bytes(response.content)  # делает тоже что и менеджер контекста with....

# with open(tmp_file, 'wb') as file:
#     file.write(response.content)

data = response.json()

print(1)
