from telebot.types import Message
from loader import bot
from loguru import logger


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
# В ответ отсылается сообщение с просьбой ввести команду /help.
@bot.message_handler(func=lambda message: Message not in ['start', 'help', 'lowprice', 'highprice',
                                                          'bestdeal', 'history'])
def bot_echo(message: Message) -> None:
    """
    Для необработанных сообщений
    :param message: Сообщение
    :return: None
    """
    logger.info(f'Пользователь {message.from_user.id}, ввел несуществующую команду.')
    bot.send_message(message.chat.id, "Я тебя не понимаю. Напиши /help.")