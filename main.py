from random import randrange

from vk_api.longpoll import VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from db_files.models import fill_status_field, fill_user_table
from functionsvk import write_msg, get_user_data, get_age, get_users_list 
from functionsvk import get_random_user, get_photo, get_photos_list
from functionsvk import check_missing_info, check_city, check_bdate 
from functionsvk import user_search, combine_user_data
from functionsvk import combine_users_data, sort_by_likes, photos_id, loop_bot
from functionsvk import longpoll
from config import rules, search_rules, input_rules, removal_rules



def main():
    list_chosen = []
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
                elif request in search_rules:                                      
                    random_choice = [] 
                    # передаем данные в таблицу user
                    fill_user_table(check_missing_info(get_user_data(user_id)))      
                    # передаем в функцию которая получяет случайную учетную запись из словаря, функцию которая объединяет данные поиска пользователей
                    random_user = get_random_user(combine_users_data(user_id), user_id)
                    random_choice.append(random_user)                                                       
                    # если id из списка random_choice не входит в список list_chosen                   
                    if random_choice[0]['id'] not in list_chosen:                                              
                        # выводим сообщение пользователю результата поиска
                        write_msg(user_id, {random_choice[0]['first_name'] + ' ' + random_choice[0]['last_name']}, None)
                        write_msg(user_id, f"Ссылка на профиль:{random_choice[0]['vk_link']}", None)
                        photos_list = get_photos_list(sort_by_likes(get_photo(random_choice[0]['id'])))
                        id_photos = f"{random_choice[0]['id']}{','.join(photos_id(sort_by_likes(get_photo(random_choice[0]['id']))))}"                        
                        if photos_list != None:
                            write_msg(user_id, None, f"{','.join(photos_list)}{id_photos}")
                        else:
                            write_msg(user_id, f"У пользователя нет фотографий(", None)  
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('да', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('нет', color=VkKeyboardColor.NEGATIVE)      
                        write_msg(user_id, f"Занести пользователя в список избранных?", None, keyboard)                      
                        # объявляем функцию сообщений
                        message_text = loop_bot()          
                        if message_text == 'да':        
                            write_msg(user_id, f"Пользователь занесен в список избранных", None) 
                            # добавляем кандидата в таблицу white_list
                            # нужно реализовать функцию которая добавляет кандидата в таблицу white_list
                            # добавляем кандидата в список избранных
                            list_chosen.append(random_choice[0]['id'])                                    
                        elif message_text == 'нет':                           
                            write_msg(user_id, f"Кандидат занесен в черный список", None)
                            # добавляем кандидата в таблицу black_list
                            # нужно реализовать функцию которая добавляет кандидата в таблицу white_list
                            list_chosen.append(random_choice[0]['id'])
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('да', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('нет', color=VkKeyboardColor.NEGATIVE)
                        keyboard.add_line()
                        keyboard.add_button('Показать избранных', color=VkKeyboardColor.POSITIVE)      
                        write_msg(user_id, f"Продолжить поиск?)\n", None, keyboard)
                    else:
                        continue
                        
                elif request == 'показать избранных':                        
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('да', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('нет', color=VkKeyboardColor.NEGATIVE)    
                    # выводим сообщение пользователю из таблици favorites
                    # нужно реализовать функцию которая выводит список избранных из таблици favorites
                    #write_msg(user_id, f"{check_db_favorites(user_id)}", None)                   
                    write_msg(user_id, f"Продолжить поиск? ", None, keyboard)
                elif request in removal_rules:
                    write_msg(user_id, "Спасибо за использование сервиса. Всего доброго!", None)
                    break
                else:
                    write_msg(user_id, "Не поняла что вы написали...", None)


if __name__ == '__main__':
    main()
