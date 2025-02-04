from loader import bot
from loguru import logger
from database.db_utils import create_table
import handlers


if __name__ == '__main__':
    logger.add("bot.log", format="{time} {level} {message}", level="DEBUG", rotation="500MB", compression="zip")
    logger.info(f'Пользователь запустил бота')
    create_table()
    bot.infinity_polling()
