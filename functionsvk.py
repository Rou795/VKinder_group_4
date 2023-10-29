import datetime
import random
from datetime import datetime
from random import randrange
from rules import requested_fields
from vk_api.longpoll import VkEventType
from config import vk, vk2, longpoll

required_info = requested_fields.copy()
required_info.extend(['domain', 'age', 'id', 'is_closed'])


def write_msg(user_id, message, attachment, keyboard=None):
    """
    Function for sending messages to user
    функция отправки сообщений пользователю
    """
    post = {'peer_id': user_id,
            'message': message,
            'attachment': attachment,
            'random_id': randrange(10 ** 7)}
    if keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post
    vk.method('messages.send', post)


def get_user_data(user_id):
    """
    gets user data by id and returns a dictionary
    получает данные пользователя по id и возвращает словарь, отправляет сообщение
    пользователю в случае ошибки.
    """
    user_data = {}
    response = vk.method('users.get', {'user_id': user_id,
                                       'v': 5.154,
                                       'fields': ','.join(requested_fields)})
    if response:
        user_data = {}
        for key, value in response[0].items():
            if key in required_info:
                if key == 'bdate':
                    user_data[key] = datetime.strptime(value, '%d.%m.%Y').date()
                else:
                    user_data[key] = value
        today = datetime.today()
        user_data['age'] = today.year - user_data['bdate'].year
    else:
        write_msg(user_id, 'Ошибка', None)
        return False

    return user_data


def check_missing_info(user_data):
    """
    collect information about missing user data and create keys for missing data
    собирает информацию о недостающих данных пользователя и создаёт ключи для недостающих данных,
    возвращает json с недостающими данными
    """
    if user_data:
        for item in ['bdate', 'city']:
            if not user_data.get(item):
                user_data[item] = ''
        if user_data.get('bdate'):
            if user_data['bdate'].year == 1900:
                user_data[item] = ''
        return user_data
    write_msg(user_data['id'], 'Ошибка', None)
    return False


def check_bdate(user_data, user_id):
    """
    Проверяет дату рождения пользователя и заполняет ее датой ввода пользователя
    в случае ошибки возвращает сообщение пользователю
    """
    if user_data:
        for item_dict in [user_data]:
            if item_dict['bdate'].year == 1900:
                write_msg(user_id, f'Введите дату рождения в формате "ХХ.ХХ.ХХХХ:"', None)
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        try:
                            user_data['bdate'] = datetime.strptime(event.text, '%d.%m.%Y')
                            return user_data
                        except ValueError:
                            write_msg(user_data['id'], 'Неправельно введенная дата', None)

            else:
                return user_data

    write_msg(user_data['id'], 'Ошибка', None)
    return False

def get_city(user_data: dict):
    resp = vk2.method('database.getCities', {
        'country_id': 1,
        'q': f'{user_data.get("city")}',
        'need_all': 0,
        'count': 1000,
        'v': 5.154})
    if resp:
        if resp.get('items'):
            user_data['city'] = {'id': resp.get('items')[0]['id'], 'title': user_data.get("city")}
    return user_data

def check_city(user_data, user_id):
    """
    Checks the user's city if there is no city
    executes data entered by the user
    Проверяет город пользователя если город отсутствует
    заполняет данные введенные пользователем 
    """
    if user_data:
        for item_dict in [user_data]:
            if item_dict['city'] is None:
                write_msg(user_id, f'Введите город:', None)
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        resp = vk2.method('database.getCities', {
                            'country_id': 1,
                            'q': f'{event.text}',
                            'need_all': 0,
                            'count': 1000,
                            'v': 5.154})
                        if resp:
                            if resp.get('items'):
                                user_data['city'] = resp.get('items')[0]['id']
                                return user_data
                            else:
                                write_msg(user_id, 'Ошибка ввода города', None)
                                write_msg(user_id, f'Введите город:', None)
            else:
                return user_data
    write_msg(user_id, 'Ошибка', None)
    return False


def get_age(user_data):
    """
    Counting users age
    считает возраста пользователей
    """
    if user_data:
        user_data['age'] = datetime.today().year - user_data['bdate'].year
        return user_data
    write_msg(user_data['id'], 'Ошибка', None)
    return False


def user_search(user_data):
    """
    Searching for pair, accordind to parameters
    Ищет пару по параметрам
    """
    resp = []
# эксперементально

    b_date = [el for el in range(1, 32)]
    b_month = [el for el in range(1, 13)]
    for birth_day in range(1, 32):
        resp.extend(vk2.method('users.search', {
        'fields': ','.join(requested_fields),
        'age_from': user_data['age'] - 3,
        'age_to': user_data['age'] + 3,
        'city': user_data.get('city').get('id'),
        'sex': 3 - user_data['sex'],
        'relation': 6,
        'has_photo': 1,
        'count': 400,
        'birth_day': birth_day,
        'v': 5.154})['items'])

    if resp:
        users = resp
        print(len(resp))
        users_data = []
        for user in users:
            user_template = {}
            if user.get('city') is None:
                continue
            else:
                if user.get('city').get('id') != user_data.get('city').get('id'):
                    continue
            for key, value in user.items():
                if key in required_info:
                    if key == 'bdate':
                        if value.count('.') == 2:
                            user_template[key] = datetime.strptime(value, '%d.%m.%Y').date()
                        elif value.count('.') == 1:
                            user_template[key] = datetime.strptime(value, '%d.%m').date()
                        else:
                            user_template[key] = value
                    else:
                        user_template[key] = value
            users_data.append(user_template.copy())
            user_template.clear()
    else:
        write_msg(user_data['id'], 'Ошибка', None)
        return False
    return users_data


def get_users_list(users_data, user_id):
    """
    Filters open user accounts
    Фильтрует открытые аккаунты пользователей
    """
    not_private_list = []
    if users_data:
        for person_dict in users_data:
            if person_dict.get('is_closed') is False:
                if person_dict.get('bdate') is not None and person_dict.get('city') is not None:
                    not_private_list.append(
                        {'first_name': person_dict.get('first_name'), 'last_name': person_dict.get('last_name'),
                         'id': person_dict.get('id'), 'vk_link': 'vk.com/id' + str(person_dict.get('id')),
                         'is_closed': person_dict.get('is_closed'), 'bdate': person_dict.get('bdate'),
                         'user_id': user_id,
                         'sex': person_dict.get('sex'), 'domain': person_dict.get('domain'),
                         'city': person_dict.get('city')
                         })
                else:
                    continue
            else:
                continue

        return not_private_list
    write_msg(user_id, 'Ошибка', None)
    return False


def combine_users_data(user_data, bd_founders=None):
    """
    Combining users search data
    объединяет данные поиска пользователей
    """
    if bd_founders:
        user_data = bd_founders
        return user_data
    else:
        users_data = get_users_list(user_search(user_data), user_data['id'])
        if users_data:
            return users_data
        else:
            write_msg(user_data['id'], 'Ошибка', None)


def get_random_user(users_data, user_id):
    """
    Getting random account from dictionary
    получает случайную учетную запись из словаря
    """
    if users_data:
        return random.choice(users_data)
    write_msg(user_id, 'Ошибка', None)
    return False


def get_photo(vk_id):
    """
    Getting photos from vk
    Получает фотографии из ВК
    """
    resp = vk2.method('photos.get', {'owner_id': vk_id,
                                     'album_id': 'profile',
                                     'extended': 1,
                                     'count': 50,  # установливаем нужное количество фото для загрузки
                                     'v': 5.154,
                                     })

    if resp:
        if resp.get('items'):
            return resp.get('items')
        else:
#            write_msg(vk_id, 'Ошибка', None)
            return False


def sort_by_likes(photos: list) -> list:
    """
    Sorting photos by number of likes
    Сортирует фотографии по количеству лайков и возвращаем первые 3 фотографии с максимальным количеством лайков
    """
    photos_by_likes_list = []

    photos_by_likes_list = sorted(photos, key=lambda x: x.get('likes').get('count'), reverse=True)
    return photos_by_likes_list[0:3]


def get_photos_list(sort_list):
    """
    we return the first 3 photos with the maximum number of likes
    возвращаем первые 3 фотографии с максимальным количеством лайков
    """
    photos_list = []
    for photos in sort_list:
        photos_list.append('photo' + str(photos.get('owner_id')) + '_' + str(photos.get('id')))
    return photos_list


def photos_id(photo_id):
    """
    gets photo IDs and returns them to the list
    получает идентификаторы фото и возвращает их в списке 
    """
    list_id = []
    for photo in photo_id:
        list_id.append(str(photo.get('id')))

    return list_id


def loop_bot():
    """
    Function for new bot messages
    Функция для новых сообщений бота
    """
    for this_event in longpoll.listen():
        if this_event.type == VkEventType.MESSAGE_NEW:
            if this_event.to_me:
                message_text = this_event.text
                return message_text
