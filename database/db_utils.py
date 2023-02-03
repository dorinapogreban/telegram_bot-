import sqlite3
from loader import bot
from loguru import logger


def create_table():
    """Функция создаёт таблицe в базу данных если её не существует."""
    with sqlite3.connect('database/history.db') as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS history_telebot (
            user_id INTEGER,
            username TEXT,
            command TEXT,
            command_date DATETIME,
            photo BLOB,
            hotels TEXT)
        """
        )
    logger.info(f'Создание базы данных.')


def update_history_db(user_id: int, username: str, command: str, command_date, photo, hotels):
    """ Сохранение данных о запросе в базу данных.
        :params user_id: id пользователя
                username: имя пользователя
                command: команду которую ввел пользователь
                command_date: дата когда была введена команда
                photo: фото отеля
                hotels: информация об отелях
    """
    with sqlite3.connect('database/history.db') as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO 'history_telebot' (user_id, username, photo, hotels, command, command_date) VALUES 
            (?, ?, ?, ?, ?, ?)
        """, (user_id, username, photo, hotels, command, command_date),
        )
    logger.info(f'Сохранение данных о запросе в базу данных.')


def get_history_db(user_id: int, chat_id: int) -> None:
    """Возвращает историю поиска последних 10 записей в базу данных с задоным id"""

    with sqlite3.connect('database/history.db') as con:
        cur = con.cursor()
        history_list = []
        cur.execute(
            """SELECT username, command, command_date, photo, hotels FROM 'history_telebot' WHERE user_id == (?)
            """, (user_id,)
        )
        result = cur.fetchall()
        if result:
            bot.send_message(chat_id, f'Вывод истории поиска отелей!')
            for res in result:
                history_str = ''
                for r in res:
                    history_str += str(r) + '  '
                history_list.append(history_str)
            for info in history_list[-10:]:
                bot.send_message(chat_id, info)
        else:
            bot.send_message(chat_id, 'Записей не обнаружено!')
    logger.info(f'Возвращает историю поиска последних 10 записей в базу данных с задоным id.')

