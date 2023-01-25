from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from loguru import logger
from handlers.custom_heandlers.history import update_history_db
from datetime import datetime


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Первое сообщение при запуске бота. Установка первоначальных данных пользователя.
    """
    logger.info(f'Пользователь {message.from_user.id}, ввел команду: /start')
    update_history_db(user_id=message.from_user.id,
                      username=message.from_user.full_name,
                      command='start',
                      command_date=datetime.now(),
                      photo=None,
                      hotels=None)
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS if command != 'start']
    bot.send_message(message.chat.id, f'Выберите команду')
    bot.send_message(message.chat.id, '\n'.join(text))
    bot.send_message(message.chat.id, 'Информацию об отелях можно посмотреть по сайту Hotels.com')
    bot.delete_state(message.from_user.id, message.chat.id)  # удаляем сохраненные данные
