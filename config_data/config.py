"""
BOT_TOKEN и RAPID_API_KEY храниться в файле .env в корневом каталоге проекта.
DEFAULT_COMMANDS - список собственных команд.
"""


import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "помощь по командам бота"),
    ('highprice', "вывод самых дорогих отелей в городе"),
    ('lowprice', "вывод самых дешёвых отелей в городе"),
    ('bestdeal', "вывод отелей, наиболее подходящих по цене и расположению от центра"),
    ('history', "вывод истории поиска отелей")
)
