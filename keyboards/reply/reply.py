from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def city_choice(cities: dict) -> ReplyKeyboardMarkup:
    """
    Клавиатура вариантов подходящих локаций.
    :param cities: словарь {Наименование_локации: ID локации}.
    :return: клавиатура
    """
    keyboard = ReplyKeyboardMarkup(True, one_time_keyboard=True, row_width=1)
    keyboard.add(*[KeyboardButton(city) for city in cities])
    return keyboard


def photo_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура вариантов если пользователь хочет получать фото отелях или нет.
    :return: Клавиатура с двумя кнопкоми..
    """
    keyboard = ReplyKeyboardMarkup(True, True, row_width=2)
    button1 = KeyboardButton('Да')
    button2 = KeyboardButton('Нет')
    keyboard.add(button1, button2)
    return keyboard


def count_photo_keyboard() -> ReplyKeyboardMarkup:
    """
    Кнопка вариантов с количеством фотографий отеля.
    :return: Клавиатура с 4 кнопкоми.
    """
    keyboard = ReplyKeyboardMarkup(True, True, row_width=4)
    button1 = KeyboardButton('1')
    button2 = KeyboardButton('5')
    button3 = KeyboardButton('10')
    button4 = KeyboardButton('15')
    keyboard.add(button1, button2, button3, button4)
    return keyboard
