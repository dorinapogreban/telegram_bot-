from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from loguru import logger
from database.db_utils import update_history_db
from datetime import datetime


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """
    Отправка списка доступных команд.
    """
    logger.info(f'Пользователь {message.from_user.id}, ввел команду: /help')
    update_history_db(user_id=message.from_user.id,
                      username=message.from_user.full_name,
                      command='help',
                      command_date=datetime.now(),
                      photo=None,
                      hotels=None)
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
