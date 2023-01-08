# from telebot.types import Message
# from loader import bot
#
#
# @bot.message_handler(commands=['/hello'])
# def get_text_messages(message: Message) -> None:
#     """
#     Реагирование бота на команду /hello, а также на текст «Привет».
#     """
#     if message.text == "/hello":
#         bot.send_message(message.from_user.id, "Привет, для получения списка команд набери /help")
#
