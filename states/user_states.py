from telebot.handler_backends import State, StatesGroup


class UserState(StatesGroup):
    """Класс UserState, Родитель: StatesGroup.
    Это Класс - машина состояний пользователя где указано количество опросов сценария."""
    city = State()  # выбор города
    count_hotels = State()  # количество отелей
    check_in = State()  # выбор даты заезда
    check_out = State()  # выбор даты выезда
    count_foto = State()  # количество фотографий
    price_max = State()  # максимальная цена
    price_min = State()  # минимальная цена
    distance = State()  # ростаяние от центра
    command = State()  # выбранная команда
    respons_foto = State()  # если пользователь хочет получать фото отелях или нет
