from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from loguru import logger


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """
    Отправка списка доступных команд.
    """
    logger.info(f'Пользователь {message.from_user.id}, ввел команду: /help')
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
