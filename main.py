from vk_api.longpoll import VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from functionsvk import (sort_by_likes, photos_id, loop_bot, get_photo, get_photos_list,
                         check_missing_info, get_user_data, get_random_user, combine_users_data, write_msg, longpoll,
                         get_city)

from rules import rules, search_rules, input_rules, removal_rules
from db_files.functionsdb import (fill_user_table, fill_black_list, fill_found_user_table,
                                  fill_favorite, check_db_favorites, check_user,
                                  take_from_bd, show_status_maker, take_from_users, check_black_list)


def show_people(peoples_for_show: list, user_data: dict, user_id: str,
                list_chosen: list, ban_list: list):
    """
    Функция для показа кандидатов для общения
    """
    if peoples_for_show:
        search_data = peoples_for_show
    else:
        bd_founders = take_from_bd(int(user_id))
        search_data = combine_users_data(user_data, bd_founders=bd_founders)
        if bd_founders:
            pass
        else:
            fill_found_user_table(search_data, int(user_id))
        peoples_for_show = search_data
    random_user = get_random_user(search_data, user_id)
    # если id из списка random_choice не входит в список list_chosen и ban_list
    marker = check_ban_chosen(random_user, list_chosen, ban_list)
    if marker:
        show_people(peoples_for_show, user_data, user_id, list_chosen, ban_list)
    else:
        showed_peoples = []
        message = (f"{random_user['first_name'] + ' ' + random_user['last_name']}\n"
                   f"Ссылка на профиль:{random_user['vk_link']}\n")
        photos_list = get_photo(random_user['id'])
        if photos_list:
            photos_list = get_photos_list(sort_by_likes(photos_list))
            id_photos = (f"{random_user['id']},"
                         f"{','.join(photos_id(sort_by_likes(get_photo(random_user['id']))))}")
            write_msg(user_id, message, f"{','.join(photos_list)},{id_photos}")
        else:
            message += f"У пользователя нет фотографий("
            write_msg(user_id, message, None)

    # метод для выставления метки "просмотренности" у человека из базы FoundUsers.
    # Должен будет работать со списком, но пока логику обработки придумали только на каждом шаге просмотра

        showed_peoples.append(random_user['id'])
        show_status_maker(int(user_id), showed_peoples)
#        return peoples_for_show, random_user
        post_search_talk(random_user, user_id, peoples_for_show, user_data, list_chosen, ban_list)


def new_user(user_id: str) -> dict:
    """
    Функция для сбора информации о новом пользователе и записи её в БД
    """
    user_data = check_missing_info(get_user_data(user_id))
    fill_user_table(user_data)
    return user_data


def old_user(user_id: str):
    """
    Функция для выгрузки информации о старом пользователе из БД.
    """
    user_data = get_city(take_from_users(int(user_id)))
    favorites = check_db_favorites(user_id)
    black_list = check_black_list(user_id)
    return user_data, favorites, black_list


def check_ban_chosen(random_user: dict, chosen_list: list, ban_list: list) -> bool:
    """
    Фугнкций проверки на то, есть ли найденный пользователь в
    списках избранных и забаненных
    """
    chosen_marker = False
    ban_marker = False
    if chosen_list:
        if random_user['id'] in chosen_list:
            chosen_marker = True
    if ban_list:
        if random_user['id'] in ban_list:
            ban_marker = True
    return chosen_marker and ban_marker


def post_search_talk(random_user: dict, user_id: str, peoples_for_show: list, user_data: dict,
                     list_chosen: list, ban_list: list) -> None:
    """
    Функция для общения с пользователем после показа человека
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('В избранные', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('В черный лист', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Продолжить поиск', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Закончить поиск', color=VkKeyboardColor.SECONDARY)
    write_msg(user_id, f"Как вам это человек?", None, keyboard)
    # объявляем функцию сообщений
    message_text = loop_bot()
    if message_text == 'В избранные':
        write_msg(user_id, f"Пользователь занесен в список избранных", None)
        # добавляем кандидата в таблицу Favorite
        fill_favorite(random_user, user_id)
        show_people(peoples_for_show, user_data, user_id, list_chosen, ban_list)
    # добавляем кандидата в список избранных
    elif message_text == 'В черный лист':
        write_msg(user_id, f"Кандидат занесен в черный список", None)
        # добавляем кандидата в таблицу black_list
        fill_black_list(random_user, int(user_id))
        show_people(peoples_for_show, user_data, user_id, list_chosen, ban_list)
    elif message_text == 'Продолжить поиск':
        show_people(peoples_for_show, user_data, user_id, list_chosen, ban_list)
    # ветка для окончания работы
    elif message_text == 'Закончить поиск':
        main_menu(user_id, peoples_for_show, list_chosen, ban_list)


def search_blok(user_data: dict, list_chosen: list,
                ban_list: list, peoples_for_show: list):
    """
    Функция, являющаяся центральным узлом для операций поиска
    """
    peoples_for_show, random_user = show_people(peoples_for_show, user_data, user_data['id'],
                                                list_chosen, ban_list)
    post_search_talk(random_user, user_data['id'], peoples_for_show, user_data, list_chosen, ban_list)


def ban_show(user_id: str, peoples_for_show: list, list_chosen: list) -> None:
    """
    Функция для показа забаненных
    """
    keyboard = VkKeyboard()
#    keyboard.add_button('да', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Выйти в главное меню', color=VkKeyboardColor.NEGATIVE)
    write_msg(user_id, f"Список забаненных", None, keyboard)
    # выводим сообщение пользователю из таблицы favorites
    ban_list = check_db_favorites(user_id)
    message = ''
    if ban_list:
        for idx, people in enumerate(ban_list):
            message += f"{idx + 1}. {''.join(people[2])}\n{''.join(people[3])}\n"
        write_msg(user_id, message, None)
    else:
        write_msg(user_id, 'В бане никого нет', None)
    message_text = loop_bot()
    if message_text == 'Выйти в главное меню':
        main_menu(user_id, peoples_for_show, list_chosen, ban_list)


def favorite_show(user_id: str, peoples_for_show: list, ban_list: list) -> None:
    """
    Функция для показа избранных
    """
    keyboard = VkKeyboard()
#    keyboard.add_button('да', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Выйти в главное меню', color=VkKeyboardColor.NEGATIVE)
    # выводим сообщение пользователю из таблицы favorites
    list_chosen = check_db_favorites(user_id)
    write_msg(user_id, f"Список избранных", None, keyboard)
    message = ''
    if list_chosen:
        for idx, people in enumerate(list_chosen):
            message += f"{idx + 1}. {''.join(people[2])}\n{''.join(people[3])}\n"
        write_msg(user_id, message, None)
    else:
        write_msg(user_id, 'В списке избранных никого нет', None)
    message_text = loop_bot()
    if message_text == 'Выйти в главное меню':
        main_menu(user_id, peoples_for_show, list_chosen, ban_list)
   
    
def main_menu(user_id, peoples_for_show: list, list_chosen: list, ban_list: list, first_text=rules):
    """
    Функция для главного меню
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Избранные', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Забаненные', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
    write_msg(user_id, first_text, None, keyboard)
    message_text = loop_bot()
    if message_text == 'Начать поиск':
        check_new = check_user(int(user_id))
        if check_new:
            write_msg(user_id, 'Для новых пользователей первичный поиск может занять около 2 минут.'
                               ' Когда придёте в следующий раз, так долго ждать не заставлю'
                               , None)
            user_data = new_user(user_id)
        else:
            user_data, list_chosen, black_list = old_user(user_id)
        if list_chosen:
            list_chosen = [el[1][3:] for el in list_chosen]
        if ban_list:
            ban_list = [el[1][3:] for el in ban_list]
#        search_blok(user_data, list_chosen, ban_list, peoples_for_show)
        show_people(peoples_for_show, user_data, user_id, list_chosen, ban_list)
    elif message_text == 'Избранные':
        favorite_show(user_id, peoples_for_show, ban_list)
    elif message_text == 'Забаненные':
        ban_show(user_id, peoples_for_show, list_chosen)
    elif message_text == 'Пока':
        write_msg(user_id, "Спасибо за использование сервиса. Всего доброго!", None)
    else:
        write_msg(user_id, "Не понял что вы написали. Я пока молод и понимаю только кнопки)", None)
        main_menu(user_id, peoples_for_show, list_chosen, ban_list, first_text)


def main():
    list_chosen = []
    ban_list = []
    peoples_for_show = []
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_id = str(event.user_id)
                request = event.text.lower()
                if request in input_rules:
                    main_menu(user_id, peoples_for_show, list_chosen, ban_list)


if __name__ == '__main__':
    main()
