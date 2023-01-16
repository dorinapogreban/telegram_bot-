import requests
from loguru import logger
import json
import re
from typing import Optional, Literal, List, Dict, Final, Any
from config_data.config import RAPID_API_KEY


def request_to_api_hotel(querystring: dict, mode: Literal['des', 'hotel', 'foto', 'address'] = 'hotel') -> Optional:
    """
    Базовая функция запроса к API Hotels
    :param mode: тип запрашиваемых данных:
                'des' - подходящие местоположения
                'hotel' - список отелей, значение по умолчанию
                'foto' - фото отелей
                'address' - адрес отелей
    :param querystring: строка запроса
    :return: код ответа, если код ответа <Response [200]>, то запрос праведён успешно
    """
    logger.info(f'Универсальноя функция {request_to_api_hotel.__name__}, аргументы: {querystring, mode}')

    url = 'https://hotels4.p.rapidapi.com/'
    headers = {'X-RapidAPI-Host': 'hotels4.p.rapidapi.com', 'X-RapidAPI-Key': RAPID_API_KEY}

    try:
        if mode == 'hotel':
            endpoint = 'properties/v2/list'
            response = requests.post(url + endpoint, headers=headers, json=querystring, timeout=50)
        elif mode == 'des':
            endpoint = 'locations/v2/search'
            response = requests.get(url + endpoint, headers=headers, params=querystring, timeout=50)
        elif mode == 'foto' or 'address':
            endpoint = 'properties/v2/detail'
            response = requests.post(url + endpoint, headers=headers, json=querystring, timeout=50)
        # print(response.status_code, requests.codes.ok)
        if response.status_code == requests.codes.ok:
            logger.info(f'Функция {request_to_api_hotel.__name__}, response.status_code: {requests.codes.ok}')
            # print('Ответ успешно получен.')
            response.encoding = 'utf-8'
            # response = response.json()
            # print(response.text)
            return response
    except requests.exceptions.RequestException as error:
        # print('Ошибка request', error)
        logger.error(f'Функция {request_to_api_hotel.__name__}, error: {error}')
        logger.debug(f'{error}')


def get_destination(location: str) -> Optional[Dict[str, str]]:
    """
    Функция получения от API Hotels местоположений, подходящих по названию.
    :param location: строка для поиска
    :return: словарь(ключ - наименование локации: значение - id локации)
    """
    logger.info(f'Функция {get_destination.__name__}, аргументы: {location}')
    querystring = {"query": location, "locale": "ru_RU", "currency": "USD"}
    response = request_to_api_hotel(querystring=querystring, mode='des')
    # print(response)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    result = {}
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        for line in suggestions['entities']:
            name = re.sub(r'<.*?>', '', line['caption'])
            result[name] = line['geoId']
    logger.info(f'Функция {get_destination.__name__}, return: {result}')
    return result


def get_hotels(data: dict) -> List[dict]:
    """
    Получает текущее состояние пользователя, формируется базовая строка запроса для получения списка отелей,
     запрашиваются отели. Формируется список с данными по отелям.
    :param data: текущие данные пользователя.
    :return: список, элемент списка - словарь с данными об отеле
    """
    logger.info(f'Функция {get_hotels.__name__}, аргументы: {data}')
    sort = ''
    destination = ''
    if data['command'] == '/lowprice':
        sort = 'PRICE_LOW_TO_HIGH'
        destination = {"regionId": data['city_id']}
    elif data['command'] == '/highprice':
        sort = 'PRICE_HIGH_TO_LOW'
        destination = {"regionId": data['city_id']}
    elif data['command'] == '/bestdeal':
        destination = {"regionId": data['city_id']}
        sort = 'DISTANCE'

    querystring: dict = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": destination,
        "checkInDate": {"day": data['check_in'].day, "month": data['check_in'].month,
                        "year": data['check_in'].year},
        "checkOutDate": {"day": data['check_out'].day, "month": data['check_out'].month,
                         "year": data['check_out'].year},
        "rooms": [{"adults": 1}],
        "resultsStartingIndex": 1,
        "resultsSize": 25,
        "sort": sort,
        "filters": {"price": {"max": data['price_max'], "min": data['price_min']}}}

    def hotel_info(hotel: dict) -> dict:
        """
        Функция которая структурирует информацию об отеле.
        :param hotel: словарь с данными об отеле
        :return: возвращает структурированную информацию об отеле.
        """
        detail = get_detail(hotel_id=str(hotel['id']))
        info_hotel = {
            'name': f"{get_star(detail)} {hotel['name']}",
            'id': hotel['id'],
            'url': f'https://www.hotels.com/h{hotel["id"]}.Hotel-Information',
            'address': get_address(address=detail),
            'price': get_price(price=hotel['price']),
            'distance': f"{hotel['destinationInfo']['distanceFromDestination']['value']}",  # км от центра города
            'latitude': hotel['mapMarker']['latLong']['latitude'],
            'longitude': hotel['mapMarker']['latLong']['longitude'],
            'photo': get_photo(id_hotel=detail, count_photo=data['count_foto'])
        }
        return info_hotel

    def get_price(price: dict) -> str:
        """
        Функция поиска цен
        :param price: словарь с данными о цене
        :return: возвращает стоимасть за однаго человека за сутки и за всего периуда.
        """
        try:
            cost = round(price['lead']['amount'])
        except (TypeError, KeyError):
            return 'Стоимость: нет данных.'
        return f'За сутки {cost}$. Всего {cost * total_day:.2f}$ за {total_day} {night}.'

    def get_address(address: dict) -> str:
        """
        Функция поиска адреса
        :param address: словарь с данными об отеля
        :return: возвращает адрес отеля, если нет данных про адрес отеля, то возвращает 'Не определен'
        """
        try:
            result_address = address['data']['propertyInfo']['summary']['location']['address']['addressLine']
        except KeyError:
            return 'Не определен'
        return result_address

    def get_star(star: dict) -> str:
        """
        Функция поиска рейтинга отеля (звёзд)
        :param star: словарь с данными об отеля
        :return: возвращает количество звёзд
        """
        star_rating: Any = star['data']['propertyInfo']['summary']['overview']['propertyRating']
        if star_rating is not None:
            star = int(star_rating['rating'])
        else:
            star = 0
        return f"{'⭐' * star}"

    def get_photo(id_hotel: dict, count_photo: int) -> list:
        """
        Функция поиска фотографии отеля
        :param id_hotel: словарь с данными об отеля
        :param count_photo: количество фотографии
        :return: возвращает список ссылок на фотографии
        """
        if count_photo > 5:
            count_photo = 5
        photo_res: list = list()

        for elem in id_hotel['data']['propertyInfo']['propertyGallery']['images']:
            url = elem['image']['url']
            photo_res.append(url)
        return photo_res[:count_photo]

    total_day: Final[int] = (data['check_out'] - data['check_in']).days
    #  переменные total_day и night используются во вложенной функции get_price
    if total_day == 1:
        night = 'ночь'
    elif total_day < 5:
        night = 'ночи'
    else:
        night = 'ночей'

    result_hotels: List = []
    page_number = 1

    while data['count_hotels'] > len(result_hotels):
        response = request_to_api_hotel(querystring=querystring, mode='hotel')
        try:
            response = json.loads(response.text)
        except json.decoder.JSONDecodeError as error:
            response = None
            # print('Ошибка request', error)
            logger.error(f'Функция {get_hotels.__name__}, error: {error}')
            logger.debug(f'{error}')
        response = response['data']['propertySearch']['properties']  # оставляем список отелей
        if data['command'] == '/bestdeal':
            if response[0]['destinationInfo']['distanceFromDestination']['value'] <= data['distance']:
                result_hotels.extend([hotel_info(hotel=hotel) for hotel in response])
                page_number += 1
                querystring.update({"resultsStartingIndex": page_number})
        else:
            result_hotels.extend([hotel_info(hotel=hotel) for hotel in response])
            page_number += 1
            querystring.update({"resultsStartingIndex": page_number})
    return result_hotels[:data['count_hotels']]


def get_detail(hotel_id: str) -> dict:
    """
    Функция получения от API Hotels данные об отеле.
    :param hotel_id: ID отеля
    :return: словарь(с данными об отеле)
    """
    logger.info(f'Функция {get_detail.__name__}, аргументы: {hotel_id}')
    querystring: dict = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": str(hotel_id)}
    response = request_to_api_hotel(querystring=querystring, mode='address')
    try:
        response = json.loads(response.text)
    except json.decoder.JSONDecodeError as error:
        # print('Ошибка request', error)
        logger.error(f'Функция {get_detail.__name__}, error: {error}')
        logger.debug(f'{error}')
    return response


# print(request_to_api_hotel(querystring={"query": 'Турция', "locale": "ru_RU", "currency": "USD"}, mode='des'))
# print(get_destination(location='Турция'))   #corect
# print(get_hotels(data={  # Corect
#     'city_id': '8281',  # get_destination(location='Турция').values(),
#     'check_in': datetime(2022, 12, 5),
#     'check_out': datetime(2022, 12, 11),
#     'count_hotels': 3,
#     'price_max': 150,
#     'price_min': 100,
#     'count_foto': 4,
#     'command': '/highprice',
#     'distance_of_center': 4}))
# print(get_detail('74799646'))    #corect
# print(get_photo(id_hotel=get_detail('37915386'), count_photo=10))    #corect
