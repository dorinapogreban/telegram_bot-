from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from loguru import logger


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Первое сообщение при запуске бота. Установка первоначальных данных пользователя.
    """
    logger.info(f'Пользователь {message.from_user.id}, запустил бота')
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS if command != 'start']
    bot.send_message(message.chat.id, f'Выберите команду')
    bot.send_message(message.chat.id, '\n'.join(text))
    bot.send_message(message.chat.id, 'Информацию об отелях можно посмотреть по сайту Hotels.com')

    bot.delete_state(message.from_user.id, message.chat.id)  # удаляем сохраненные данные
