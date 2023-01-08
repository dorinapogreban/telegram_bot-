from loader import bot
import handlers
from utils.set_bot_commands import set_default_commands
from telebot import custom_filters


if __name__ == '__main__':
    bot.infinity_polling()
