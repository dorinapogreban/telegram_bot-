import time

from loader import bot
from telebot.types import CallbackQuery, Message, InputMediaPhoto
from keyboards.reply.reply import photo_keyboard, city_choice, count_photo_keyboard
from states.user_states import UserState
from utils.api_hotels import get_destination, get_hotels
from datetime import date, datetime
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from loguru import logger
from handlers.custom_heandlers.history import update_history_db


@logger.catch()
@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def bot_command(message: Message) -> None:
    """
    Отправка пользователю локаций, подходящих под его запрос, для уточнения.
    :param message: сообщение пользователя (название города, введенного пользователем для поиска).
    :return: None
    """
    bot.set_state(message.from_user.id, UserState.command, message.chat.id)
    command = message.text
    logger.info(f'Пользователь {message.from_user.id}, ввел команду: {command}')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = command
        data['command_date'] = datetime.now()
    bot.send_message(message.from_user.id, 'Получаем информацию...')
    bot.set_state(message.from_user.id, UserState.city, message.chat.id)
    bot.send_message(message.chat.id, 'Введите город для поиска:')


@logger.catch()
@bot.message_handler(state=UserState.city)
def get_city(message: Message) -> None:
    """
    Отправка пользователю локаций, подходящих под его запрос, для уточнения.
    :param message: сообщение пользователя (название города, введенного пользователем для поиска).
    :return: None
    """
    city = message.text
    cities = get_destination(city)
    if cities is None:
        bot.send_message(message.chat.id, f'По запросу "{city}" ничего не найдено.\n'
                                          f'Попробуйте еще раз.\n'
                                          f'Введите город для поиска:')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = cities
    if message.text in cities:
        logger.info(f'Пользователь {message.from_user.id}, выбрал гоод: {message.text}')
        # Если текст соответствует словарю, то в city сохраняем город, в city_id его id
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_id'] = cities[message.text]
            data['city'] = message.text
        # запрос даты заезда
        bot.set_state(message.from_user.id, UserState.check_in, message.chat.id)
        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).build()
        bot.send_message(message.chat.id, f"Выберите даду заезда {LSTEP[step]}", reply_markup=calendar)
    else:
        bot.send_message(message.chat.id, 'Уточните поиск:', reply_markup=city_choice(cities))


@logger.catch()
@bot.callback_query_handler(state=UserState.check_in, func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_calendar_1(call: CallbackQuery) -> None:
    """
    Отправка пользователю клавиатуру с календарём для выбора даты заезда в отель.
    :param call: сообщение пользователя (день, месяц, год заезда в отель).
    :return: None
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        logger.info(f'Пользователь {call.message.from_user.id}, выбрал даду заезда: {result}')
        bot.edit_message_text(f"Вы выбрали даду заезда {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_in'] = result
        # запрос даты выезда
        bot.set_state(call.from_user.id, UserState.check_out, call.message.chat.id)
        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=result).build()
        bot.send_message(call.message.chat.id, f"Теперь выберите дату выезда {LSTEP[step]}", reply_markup=calendar)


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_calendar_2(call: CallbackQuery) -> None:
    """
    Отправка пользователю клавиатуру с календарём, для выбора даты выезда в отель.
    Пользователь не может выбрать дату выезда раньше даты заезда.
    :param call: сообщение пользователя (день, месяц, год выездав отель).
    :return: None
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru',
                                                 min_date=date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_out'] = result
        if data['check_out'] > data['check_in']:
            logger.info(f'Пользователь {call.message.from_user.id}, выбрал даду выезда: {result}')
            bot.edit_message_text(f"Вы выбрали дату выезда {result}",
                                  call.message.chat.id,
                                  call.message.message_id)

            bot.set_state(call.from_user.id, UserState.count_hotels, call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Введите количество отелей')
        else:
            calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=data['check_in']).build()
            result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru',
                                                         min_date=data['check_in']).process(call.data)
            bot.edit_message_text(f"Вы выбрали дату выезда меньше даты заезда. \n"
                                  f"Выберите еще раз дату выезда {LSTEP[step]}",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=calendar)


@logger.catch()
@bot.message_handler(state=UserState.count_hotels)
def get_count_hotels(message: Message) -> None:
    """
    Обработка сообщение пользователя с количество отеляй для поиска.
    :param message: сообщение пользователя (количество отеляй).
    :return: None
    """
    if message.text.isdigit() and 0 < int(message.text) <= 25:
        logger.info(f'Пользователь {message.from_user.id}, выбрал даду выезда: {int(message.text)}')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_hotels'] = int(message.text)
        bot.set_state(message.from_user.id, UserState.respons_foto, message.chat.id)
        bot.send_message(message.chat.id, 'Вы хотите получить фото отеля?', reply_markup=photo_keyboard())
    else:
        bot.send_message(message.chat.id, "Количество отелей может быть только натуральным числом не больше 25!\n"
                                          "Введите ещё раз количество отелей")


@logger.catch()
@bot.message_handler(state=UserState.respons_foto)
def get_result_foto(message: Message) -> None:
    """
    Отправка пользователю клавиатуру с вариантов если пользователь хочет получать фото отелях или нет
    и обработка сообщение пользователя.
    :param message: сообщение пользователя (Да или Нет).
    :return: None
    """
    bot.set_state(message.from_user.id, UserState.count_foto, message.chat.id)
    if message.text == 'Да':
        bot.send_message(message.chat.id, 'Выберите количество выводимых фото', reply_markup=count_photo_keyboard())
    elif message.text == 'Нет':
        logger.info(f'Пользователь {message.from_user.id}, не хочет получить фото отеля')
        bot.send_message(message.chat.id, 'Вы не хотите получить фото отеля.')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_foto'] = 5  # количество фото по умолчанию
        bot.set_state(message.from_user.id, UserState.price_min, message.chat.id)
        bot.send_message(message.chat.id, 'Введите минимальную цену за день в $>>>')


@logger.catch()
@bot.message_handler(state=UserState.count_foto)
def get_count_foto(message: Message) -> None:
    """
    Обработка сообщение пользователя с количество фото отеляй.
    :param message: сообщение пользователя (количество фото отеляй).
    :return: None
    """
    if int(message.text) == 1 or 5 or 10 or 15:
        logger.info(f'Пользователь {message.from_user.id}, хочет получить {int(message.text)} фото отеля')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_foto'] = int(message.text)
        bot.set_state(message.from_user.id, UserState.price_min, message.chat.id)
        bot.send_message(message.chat.id, 'Введите минимальную цену за день в $:')


@logger.catch()
@bot.message_handler(state=UserState.price_min)
def get_min_price(message: Message) -> None:
    """
    Обработка сообщение пользователя с минимальной цены за день в $.
    :param message: сообщение пользователя (минимальную цену за день в $).
    :return: None
    """
    if message.text.isdigit():
        min_price = int(message.text)
        if int(message.text) == 0:
            min_price = 1
        elif int(message.text) > 0:
            min_price = int(message.text)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_min'] = min_price
        logger.info(f'Пользователь {message.from_user.id}, выброл минимальную цену за день в $: {min_price}')
        bot.set_state(message.from_user.id, UserState.price_max, message.chat.id)
        bot.send_message(message.chat.id, 'Введите максимальную цену за день в $:')
    else:
        bot.send_message(message.chat.id, 'Некорректный ввод, введите минимальную цену')


@logger.catch()
@bot.message_handler(state=UserState.price_max)
def get_max_price(message: Message) -> None:
    """
    Обработка сообщение пользователя с максимальной цены за день в $. Если команда '/lowprice' или '/highprice'
    обрабатываем полученную информацию от пользователя и отправления данных об отелях.
    :param message: сообщение пользователя (максимальное цена за день в $).
    :return: None
    """
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_max'] = int(message.text)
        if data['price_max'] > data['price_min']:
            logger.info(f"Пользователь {message.from_user.id}, выброл максимальную цену за день в $:"
                        f" {data['price_max']}")
            bot.send_message(message.chat.id, f"Вы выбрали диапазон цен {data['price_min']} - {data['price_max']} $")
            if data['command'] == '/bestdeal':
                bot.set_state(message.from_user.id, UserState.distance, message.chat.id)
                bot.send_message(message.chat.id, 'Введите максимальное расстояние от центра (км):')
            elif data['command'] == '/lowprice' or '/highprice':
                logger.info(f"Бот обрабатывает результат по команде: {data['command']}")
                bot.send_message(message.chat.id, 'Просим вас подождать, обрабатывается результат!')
                hotels = get_hotels(data=data)
                bot.send_message(message.chat.id, f"Данные об отелях:")
                send_hotels(hotels=hotels,
                            user_id=message.from_user.id,
                            username=message.from_user.full_name,
                            data=data)
                logger.info(f"Пользователь {message.from_user.id}, получил информацию по команде: {data['command']}")
        else:
            bot.send_message(message.chat.id, 'Максимальноя цена не может быть больше минимальной цене! '
                                              '\nВведите максимальную цену за день в $:')
    else:
        bot.send_message(message.chat.id, 'Некорректный ввод, введите максимальную цену')


@logger.catch()
@bot.message_handler(state=UserState.distance)
def get_distance(message: Message) -> None:
    """
    Обработка сообщение пользователя с максимальной расстояние от центра (км).
    Обрабатываем полученную информацию от пользователя и отправления данных об отелях.
    :param message: сообщение пользователя (максимальной расстояние от центра (км)).
    :return: None
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['distance'] = int(message.text)
    if 0 <= int(message.text) <= 50:
        logger.info(f"Пользователь {message.from_user.id}, выброл максимальное расстояние от центра (км):"
                    f"{int(message.text)}")
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['distance'] = int(message.text)
        logger.info(f"Бот обрабатывает результат по команде: {data['command']}")
        bot.send_message(message.chat.id, 'Просим вас подождать, обрабатывается результат!')
        hotels = get_hotels(data=data)
        bot.send_message(message.chat.id, f"Данных об отелях:")
        send_hotels(hotels=hotels, user_id=message.from_user.id, username=message.from_user.full_name, data=data)
        logger.info(f"Пользователь {message.from_user.id}, получил информацию по команде: {data['command']}")
    else:
        bot.send_message(message.chat.id, "Некорректный ввод, введите максимальное расстояние от центра (км):")


@logger.catch()
def send_hotels(hotels: list, user_id: int, username: str, data: dict) -> None:
    """
    Отправка данных об отелях пользователю.
    :param hotels: список словарей с данными об отелях
    :param user_id: ID пользователя
    :return: None
    """
    for hotel in hotels:
        text = f"Название отеля: {hotel['name']}\n" \
               f"Aдрес: {hotel['address']}\n" \
               f"Цена: {hotel['price']}\n" \
               f"Расстояние от центра города: {hotel['distance']} км\n" \
               f"Широта: {hotel['latitude']}\n" \
               f"Долгота: {hotel['longitude']}\n" \
               f"URL-адрес: {hotel['url']}\n\n\n"
        if not hotel['photo']:
            bot.send_message(user_id, 'Фотографий не найдено!')
        else:
            photo_list = []
            for photo in hotel['photo']:
                photo_list.append(InputMediaPhoto(media=photo, caption=text, parse_mode='HTML'))
            bot.send_media_group(user_id, photo_list)
        bot.send_message(user_id, text)
        time.sleep(0.5)
        photo = ''
        for ph in range(len(hotel['photo'])):
            photo += str(hotel['photo'][ph]) + ' '
        update_history_db(user_id=user_id,
                          username=username,
                          command=data['command'],
                          command_date=data['command_date'],
                          photo=photo,
                          hotels=text)
