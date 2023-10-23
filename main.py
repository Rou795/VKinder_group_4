from random import randrange

from vk_api.longpoll import VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
#from models import fill_status_field
from functionsvk import write_msg, get_user_data, get_age, get_users_list 
from functionsvk import get_random_user, get_photo, get_photos_list
from functionsvk import check_missing_info, check_city, check_bdate 
from functionsvk import user_search, combine_user_data
from functionsvk import combine_users_data, sort_by_likes, photos_id, loop_bot
from functionsvk import longpoll


def main():
    # if not database_exists(engine.url):
    #     create_database(engine.url)
    # create_tables(engine)
    list_chosen = []
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_id = str(event.user_id)
                request = event.text.lower()
                if request in ['привет', 'приветствую', 'hi', 'hello','здарова', 'здравствуйте', 'приветики']:                               
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_line()
                    keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
                    # передаем в функцию которая заполняет таблицу user, функцию которая объединяет данные поиска пользователей
                    #fill_user_table(combine_user_data(user_id))
                    # выводим сообщение с параматрами использования бота
                    write_msg(user_id,
                              f"Вас приветствует бот VKinder!\n"
                              f"Бот осуществляет поиск подходящей по критериям пары и заносит в список избранных или "
                              f" в черный список по указанию пользователя.\n"
                              f"Критерии: город пользователя, возраст в промежутке от -3 лет до +3 лет"
                              f" от возраста пользователя.\n"
                              f"Чтобы начать поиск нажмите кнопку 'начать поиск'.\n"
                              f"Для окончания работы с ботом нажмите кнопку 'пока',"
                              f" либо нажмите кнопку 'нет' при вопросе о продолжении поиска."
                              , None, keyboard)
                elif request =='начать поиск':                   
                    random_choice = []
                    # передаем в функцию которая получяет случайную учетную запись из словаря, функцию которая объединяет данные поиска пользователей
                    get_random_user_data = get_random_user(combine_users_data(user_id), user_id)
                    random_choice.append(get_random_user_data)
                    # пердаем в функцию которая заполняет таблицу search, список случайных пользователей
                    #fill_user_search_table([get_random_user_data], user_id)
                    # если id из списка random_choice не входит в список list_chosen
                    
                    if random_choice[0]['id'] not in list_chosen:
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
                        # выводим сообщение пользователю результата поиска
                        write_msg(user_id, {random_choice[0]['first_name'] + ' ' + random_choice[0]['last_name']}, None)
                        write_msg(user_id, f"Ссылка на профиль:{random_choice[0]['vk_link']}", None)
                        photos_list = get_photos_list(sort_by_likes(get_photo(random_choice[0]['id'])))
                        id_photos = f"{random_choice[0]['id']}{','.join(photos_id(sort_by_likes(get_photo(random_choice[0]['id']))))}"
                        write_msg(user_id, None, f"{','.join(photos_list)}{id_photos}")
                        write_msg(user_id, f"Занести пользователя в список избранных?", None, keyboard)
                        # объявляем функцию сообщений
                        message_text = loop_bot()
                        status = 0
                        if message_text == 'да':
                            
                            write_msg(user_id, f"Кандидат занесен в список избранных", None)
                            # добавляем кандидата в таблицу white_list
                            status = 1
                            # добавляем кандидата в список избранных
                            list_chosen.append(random_choice[0]['id'])
                        elif message_text == 'нет':                           
                            #write_msg(user_id, f"Кандидат занесен в черный список", None)
                            # добавляем кандидата в таблицу black_list
                            # добавляем кандидата в список избранных
                            list_chosen.append(random_choice[0]['id'])
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
                        keyboard.add_line()
                        keyboard.add_button('Показать избранных', color=VkKeyboardColor.POSITIVE)    
                        #fill_status_field(random_choice[0]['id'], status)
                        write_msg(user_id, f"Продолжить поиск?)\n", None, keyboard)
                    else:
                        continue

                elif request == 'показать избранных':
                    # выводим сообщение пользователю из таблици favorites
                    #write_msg(user_id, f"{check_db_favorites(user_id)}", None)
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
                    write_msg(user_id, f"Продолжить поиск? ", None, keyboard)
                elif request in ['пока', 'нет']:
                    write_msg(user_id, "Спасибо за использование сервиса. Всего доброго!", None)
                    break
                else:
                    write_msg(user_id, "Не поняла вашего ответа...", None)

if __name__ == '__main__':
    main()
