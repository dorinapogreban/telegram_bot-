from loader import bot
from telebot.types import Message
from datetime import datetime
from loguru import logger
from database.db_utils import update_history_db, get_history_db


@logger.catch()
@bot.message_handler(commands=['history'])
def get_history(message: Message):
    """Возвращает историю поиска последних 10 записей в базу данных с задоным id"""
    logger.info(f'Пользователь {message.from_user.id}, ввел команду: /history')

    update_history_db(user_id=message.from_user.id,
                      username=message.from_user.full_name,
                      command='/history',
                      command_date=datetime.now(),
                      photo=None,
                      hotels=None)
    get_history_db(user_id=message.from_user.id, chat_id=message.chat.id)
