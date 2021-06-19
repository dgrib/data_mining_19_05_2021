from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


if __name__ == '__main__':
    url = 'https://habr.com/ru/'
    gecko = os.path.normpath(os.path.join(os.path.dirname(__file__), 'geckodriver'))

    binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
    browser = webdriver.Firefox(firefox_binary=binary, executable_path=gecko + '.exe')
    # browser = webdriver.Firefox(firefox_binary='')  # в ключ firefox_binary указатьь путь к вубдрайверу бинарнику скачваному
    # и он будет работать с ним, это если проблемы возникают
    browser.get(url)  # никакие параметры и заголовки передавать ненадо,
    # у нас открывается браузер а селениум это просто транслятор команд, у нас уже все етсь, браузер все понимает
    # пока страница не была отрендерена, пока нам не вернулось состояние что страница загружена и больше ничего
    # не происхзодит с подзагрузками, до этого момента код будет висеть
    # (ожидать пока browser.get отработает и вернет управление потоку) минусы: парсинг на селениум - очень медленно
    # так как открывается процесс браузера, процесс окна ,каждая вкладка этол отдельный процесс
    # если выберете движок браузера хром, то будет на 30-40% прожорливее чем firefox, deckodriver он немного пошустрее
    # плюсы: если запрос сделан скриптом то ненадо ничего искать - эти запросы сделал браузер уже. Еще.
    # Все трекеры которые висят они вас отслеживают и системам которые занимаются блокиров. сложнее опред. что вы бот.

    # так как селениум для тестеров - то ловит кучу исключений
    print(1)
