from vk_api.longpoll import VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from functionsvk import (sort_by_likes, photos_id, loop_bot, get_photo, get_photos_list,
                         check_missing_info, get_user_data, get_random_user, combine_users_data, write_msg, longpoll)

from rules import rules, search_rules, input_rules, removal_rules
from db_files.functionsdb import (fill_user_table, fill_black_list, fill_found_user_table,
                                  fill_favorite, check_db_favorites, check_user, take_from_bd, show_status_maker)


def search_talk(random_user: dict, user_id: str) -> None:
    showed_peoples = []
    message = (f"{random_user['first_name'] + ' ' + random_user['last_name']}\n"
               f"Ссылка на профиль:{random_user['vk_link']}\n")
    photos_list = get_photos_list(sort_by_likes(get_photo(random_user['id'])))
    if photos_list:
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
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('да', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('нет', color=VkKeyboardColor.NEGATIVE)
    write_msg(user_id, f"Занести пользователя в список избранных?", None, keyboard)
    # объявляем функцию сообщений
    message_text = loop_bot()
    if message_text == 'да':
        write_msg(user_id, f"Пользователь занесен в список избранных", None)
        # добавляем кандидата в таблицу white_list
        fill_favorite(random_user, user_id)
    # добавляем кандидата в список избранных
    #    list_chosen.append(random_user['id'])
    elif message_text == 'нет':
        write_msg(user_id, f"Кандидат занесен в черный список", None)
        # добавляем кандидата в таблицу black_list
        fill_black_list(random_user, int(user_id))
    #    list_chosen.append(random_user['id'])


#def del_favorite_show():


def main():
    list_chosen = []
    peoples_for_show = []
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_id = str(event.user_id)
                request = event.text.lower()

                if request in input_rules:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('начать поиск', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_line()
                    keyboard.add_button('пока', color=VkKeyboardColor.NEGATIVE)
                    # выводим сообщение с параматрами использования бота
                    write_msg(user_id, rules, None, keyboard)
                    # проверяем наличе пользователя в базе. Если его нет, то добавляем
                    # информацию о нем в таблицу
                    check_new = check_user(int(user_id))
                    if check_new:
                        fill_user_table(check_missing_info(get_user_data(user_id)))
                    else:
                        favorites = check_db_favorites(user_id)
                        if favorites:
                            list_chosen = [el[1][3:] for el in check_db_favorites(user_id)]
                elif request in search_rules:
                    # передаем в функцию которая получяет случайную учетную запись из словаря,
                    # функцию которая объединяет данные поиска пользователей
                    if peoples_for_show:
                        search_data = peoples_for_show
                    else:
                        bd_founders = take_from_bd(int(user_id))
                        search_data = combine_users_data(user_id, bd_founders=bd_founders)
                        if bd_founders:
                            pass
                        else:
                            fill_found_user_table(search_data, int(user_id))
                        peoples_for_show = search_data
                    random_user = get_random_user(search_data, user_id)
                    # если id из списка random_choice не входит в список list_chosen
                    if list_chosen:
                        if random_user['id'] not in list_chosen:
                            search_talk(random_user, user_id)
                        else:
                            continue
                    else:
                        search_talk(random_user, user_id)
                    peoples_for_show.remove(random_user)
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('да', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('нет', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_line()
                    keyboard.add_button('Показать избранных', color=VkKeyboardColor.POSITIVE)
                    write_msg(user_id, f"Продолжить поиск?)\n", None, keyboard)

                elif request == 'показать избранных':
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('да', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('нет', color=VkKeyboardColor.NEGATIVE)
                    # выводим сообщение пользователю из таблицы favorites
                    favorites = check_db_favorites(user_id)
                    message = ''
                    for people in favorites:
                        message += f"# {''.join(people[2])}\n{''.join(people[3])}\n"
                    write_msg(user_id, message, None)
                    write_msg(user_id, f"Продолжить поиск? ", None, keyboard)
                elif request in removal_rules:
                    write_msg(user_id, "Спасибо за использование сервиса. Всего доброго!", None)
                    break
                else:
                    write_msg(user_id, "Не поняла что вы написали...", None)

if __name__ == '__main__':
    main()
