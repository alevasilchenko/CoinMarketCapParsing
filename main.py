from selenium import webdriver
import bs4
from time import sleep
from decimal import *
import datetime
import csv

# При GET-запросе, отправленном по адресу заданного в ТЗ сайта с помощью библиотеки requests, возвращается html-код,
# отличный от того, что мы видим непосредственно с использованием средств просмотра в браузере.
# Причиной этого является наличие в html-коде страницы скриптов.
# Только после их выполнения мы можем получить доступ к интересующим нас элементам сайта.
# Поэтому было принято решение использовать библиотеку selenium,
# позволяющую загрузить требуемую страницу в браузере в автоматическом режиме.

url = 'https://coinmarketcap.com/ru'  # url-адрес сайта, подлежащего парсингу

# создаём функцию, осуществляющую парсинг заданного сайта и возвращающую словарь, хранящий
# название первых 100 криптовалют и текущую рыночную капитализацию каждой криптовалюты


def write_cmc_top() -> dict:
    web_driver = webdriver.Chrome()  # используем веб-драйвер браузера Google Chrome
    web_driver.get(url)  # загружаем в браузер заданный сайт
    web_driver.maximize_window()  # открываем окно браузера на весь экран

    # пролистываем в цикле страницу сайта в браузере и выполняем имеющиеся скрипты (с небольшой задержкой):
    px = 0
    for _ in range(10):
        px += 1000
        web_driver.execute_script(f'window.scrollTo(0, {px})')
        sleep(0.1)

    html = web_driver.page_source  # получаем "корректный" html-код заданного сайта
    web_driver.close()  # закрываем окно браузера

    soup = bs4.BeautifulSoup(html, 'html.parser')  # преобразуем html-код сайта в объект BeautifulSoup
    cmc_table = soup.find('tbody').find_all('tr')  # извлекаем таблицу 100 криптовалют по соответствующим ей тегам

# в таблице криптовалют 11 колонок; нас интересуют колонки с индексами 2 (наименование) и 7 (капитализация)

    name_capitalization = {}  # создаём пустой словарь, который далее в цикле будем пополнять данными с сайта

    for tr in cmc_table:  # для каждой из 100 строк таблицы
        try:
            all_td = list(tr.find_all('td'))  # получаем список значений полей таблицы по соответствующим тегам
            name = all_td[2]  # получаем тег, содержащий наименование криптовалюты
            name = name.find_all('p')[0].get_text()  # извлекаем собственно наименование криптовалюты
            capitalization = all_td[7]  # получаем тег, содержащий информацию о капитализации криптовалюты
            capitalization = capitalization.find_all('span')[1].get_text()  # извлекаем собственно капитализацию
            name_capitalization[name] = capitalization  # добавляем полученную информацию в словарь
        except IndexError as e:
            print(e)
    return name_capitalization


list_name = []  # список наименований криптовалют
list_capitalization = []  # список значений рыночной капитализации каждой криптовалюты
list_part = []  # список процентов от общей капитализации каждой криптовалюты

sum_capitalization = 0  # совокупная рыночная капитализация первых 100 криптовалют

dict_name_capitalization = write_cmc_top()  # производим парсинг и получаем актуальную информацию о криптовалютах

for key, value in dict_name_capitalization.items():
    list_name.append(key)  # пополняем список наименований
    value_cap = int(value[1:].replace(',', ''))  # убираем символ валюты и запятые и преобразуем в целое
    list_capitalization.append(value_cap)  # пополняем список значений капитализации
    sum_capitalization += value_cap  # пополняем общую сумму

sum_part = 0  # переменная для контроля правильности суммы всех долей (должна быть близка к 100%)

for i in range(len(list_name)):
    part_cap = Decimal(100 * list_capitalization[i] / sum_capitalization)  # используем тип данных Decimal
    list_part.append(part_cap.quantize(Decimal('1.000')))
    sum_part += list_part[i]

file_name = str(datetime.datetime.now().strftime("%H.%M %d.%m.%Y")) + '.csv'  # формируем имя файла согласно ТЗ

with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:  # записываем результаты в CSV-файл
    writer = csv.writer(csv_file, delimiter=' ')
    header = ['Name', 'MC', 'MP']
    writer.writerow(header)
    for i in range(len(list_name)):
        row = [list_name[i], '₽' + '{:,}'.format(list_capitalization[i]), (str(list_part[i]) + '%')]
        writer.writerow(row)

print(f'\nОкруглённая сумма всех долей составила: {sum_part}% (для контроля, должна быть близка к 100%)')
