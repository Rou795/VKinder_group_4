import random
from random import randrange
import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import token_group, token_user


# Ссылки на токены
# токен группы
vk = vk_api.VkApi(token=token_group)
# токен пользователя
vk2 = vk_api.VkApi(token=token_user)
longpoll = VkLongPoll(vk)

def write_msg(user_id, message, attachment):
    """
    Function for sending messages to user
    функция отправки сообщений пользователю
    """
    vk.method('messages.send',
              {'user_id': user_id, 'message': message, 'attachment': attachment,  'random_id': randrange(10 ** 7)})

def get_user_data(user_id):
    """
    gets user data by id and returns a dictionary
    получает данные пользователя по id и возвращает словарь, отправляет сообщение
    пользователю в случае ошибки.
    """
    user_data = {}
    resp = vk.method('users.get', {'user_id': user_id,
                                   'v': 5.131,
                                   'fields': 'first name, last name, bdate, sex, city'})
    if resp:
        for key, value in resp[0].items():
            if key == 'city':
                user_data[key] = value['id']
            else:
                user_data[key] = value
    else:
        write_msg(user_id, 'Ошибка', None)
        return False
    
    return user_data

def check_missing_info(user_data):
    """
    collect information about missing user data and create keys for missing data
    собирате информацию о недостающих данных пользователя и создаёт ключи для недостающих данных,
    возвращает json с недостающими данными
    """
    if user_data:
        for item in ['bdate', 'city']:
            if not user_data.get(item):
                user_data[item] = ''
        if user_data.get('bdate'):
            if len(user_data['bdate'].split('.')) != 3:
                user_data[item] = ''
        return user_data
    write_msg(user_data['id'], 'Ошибка', None)
    return False


"""Checking user birthday date and filling it with user input date."""


def check_bdate(user_data, user_id):
    """
    Проверяет дату рождения пользователя и заполняет ее датой ввода пользователя
    в случае ошибки возвращает сообщение пользователю
    """
    if user_data:
        for item_dict in [user_data]:
            if len(item_dict['bdate'].split('.')) != 3:
                write_msg(user_id, f'Введите дату рождения в формате "ХХ.ХХ.ХХХХ:"', None)
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        user_data['bdate'] = event.text
                        return user_data
            else:           
                return user_data
    write_msg(user_data['id'], 'Ошибка', None)
    
    return False

def city_id(city_name):
    """
    Function to transform city name into city id
    Функция преобразования названия города в идентификатор города
    при ошибке возвращает сообщение пользователю
    """
    resp = vk2.method('database.getCities', {
                    'country_id': 1,
                    'q': f'{city_name}',
                    'need_all': 0,
                    'count': 1000,
                    'v': 5.131})
    if resp:
        if resp.get('items'):
            return resp.get('items')
        write_msg(city_name, 'Ошибка ввода города', None)
        return False

def check_city(user_data, user_id):
    """
    Checks the user's city if there is no city
    executes data entered by the user
    Проверяет город пользователя если город отсутствует
    заполняет данные введенные пользователем 
    """
    if user_data:
        for item_dict in [user_data]:
            if item_dict['city'] == '':
                write_msg(user_id, f'Введите город:', None)
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        user_data['city'] = city_id(event.text)[0]['id']
                        return user_data
            else:
                return user_data
    write_msg(user_data['id'], 'Ошибка', None)
    return False

def get_age(user_data):
    """
    Counting users age
    считает возраста пользователей
    """
    if user_data:
        for key, value in user_data:
            user_data['age'] = datetime.datetime.now().year - int(user_data['bdate'][-4:])
            return user_data
    write_msg(user_data['id'], 'Ошибка', None)
    return False

def user_search(user_data):
    """
    Searching for pair, accordind to parameters
    Ищет пару по параметрам
    """
    resp = vk2.method('users.search', {
                                'age_from': user_data['age'] - 3,
                                'age_to': user_data['age'] + 3,
                                'city': user_data['city'],
                                'sex': 3 - user_data['sex'],
                                'relation': 6,
                                'status': 1,
                                'has_photo': 1,
                                'count': 1000,
                                'v': 5.131})
    if resp:
        if resp.get('items'):
            return resp.get('items')
        write_msg(user_data['id'], 'Ошибка', None)
        return False

def get_users_list(users_data, user_id):
    """
    Filters open user accounts
    Фильтрует открытые акаунты пользователей
    """
    not_private_list = []
    if users_data:
        for person_dict in users_data:
            if person_dict.get('is_closed') == False:
                not_private_list.append(
                                {'first_name': person_dict.get('first_name'), 'last_name': person_dict.get('last_name'),
                                 'id': person_dict.get('id'), 'vk_link':   'vk.com/id'+str(person_dict.get('id')),
                                 'is_closed': person_dict.get('is_closed')
                                 })
            else:
                continue
        return not_private_list
    write_msg(user_id, 'Ошибка', None)
    return False

def combine_user_data(user_id):
    """
    Combining user data
    Объединяет пользовательские данные
    """
    user_data = [get_age(check_city(check_bdate(check_missing_info(get_user_data(user_id)), user_id), user_id))]
    if user_data:
        return user_data
    write_msg(user_id, 'Ошибка', None)
    return False

def combine_users_data(user_id):
    """
    Combining users search data
    объединяет данные поиска пользователей
    """
    users_data = get_users_list(
        user_search(get_age(check_city(check_bdate(check_missing_info(get_user_data(user_id)), user_id), user_id))), user_id)
    if users_data:
        return users_data
    write_msg(user_id, 'Ошибка', None)
    return False

def get_random_user(users_data, user_id):
    """
    Getting random account from dictionary
    получяет случайную учетную запись из словаря
    """
    if users_data:
        return random.choice(users_data)
    write_msg(user_id, 'Ошибка', None)
    return False

def get_photo(vk_id):
    """
    Getting photos from vk
    Получяет фотографии из ВК
    """
    resp = vk2.method('photos.get', {'owner_id': vk_id,
            'album_id': 'profile',
            'extended': 1,
            'count': 100,  # установливаем нужное количество фото для загрузки
            'v': 5.131,
            })
   
    if resp:
        if resp.get('items'):
            return resp.get('items')
        write_msg(vk_id, 'Ошибка', None)
        return False
    

def sort_by_likes(photos_dict):
    """
    Sorting photos by number of likes
    Сортирует фотографии по количеству лайков и возвращаем первые 3 фотографии с максимальным количеством лайков
    """
    photos_by_likes_list = []

    for photos in photos_dict:
        likes = photos.get('likes')
        photos_by_likes_list.append([photos.get('owner_id'), photos.get('id'), likes.get('count')])
    photos_by_likes_list = sorted(photos_by_likes_list, key=lambda x: x[2], reverse=True)
    return photos_by_likes_list[0:3]

def get_photos_list(sort_list):
    """
    we return the first 3 photos with the maximum number of likes
    возвращаем первые 3 фотографии с максимальным количеством лайков
    """
    photos_list = []
    count = 0
    for photos in sort_list:
        photos_list.append('photo'+str(photos[0])+'_'+str(photos[1]))
        count += 1
        if count == 3:
            return photos_list

def photos_id(photo_id):
    """
    gets photo IDs and returns them to the list
    получает идентификаторы фото и возвращает их в списке 
    """
    list_id = []
    for photo in photo_id:
        list_id.append(str(photo[1]))
        
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
            

           