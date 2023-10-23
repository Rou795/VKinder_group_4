from random import randrange
from config import token_group, token_user
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from db_files.models import fill_status_field
from functionsvk import *


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
                if request == 'привет':
                    # передаем в функцию которая заполняет таблицу user, функцию которая объединяет данные поиска пользователей
                    #fill_user_table(combine_user_data(user_id))
                    # выводим сообщение с параматрами использования бота
                    write_msg(user_id,
                              f"Вас приветствует бот VKinder!\n"
                              f"Бот осуществляет поиск подходящей по критериям пары и заносит в список избранных или "
                              f" в черный список по указанию пользователя.\n"
                              f"Критерии: город пользователя, возраст в промежутке от -3 лет до +3 лет"
                              f" от возраста пользователя.\n"
                              f"Чтобы начать поиск введите команду 'начать поиск'.\n"
                              f"Для вывода списка избранных введите команду 'показать избранных'.\n"
                              f"Для окончания работы с ботом введите команду 'пока',"
                              f" либо напишите 'нет' при вопросе о продолжении поиска."
                              , None)
                elif request in ['начать поиск', 'продолжить поиск', 'да']:
                    random_choice = []
                    # передаем в функцию которая получяет случайную учетную запись из словаря, функцию которая объединяет данные поиска пользователей
                    get_random_user_data = get_random_user(combine_users_data(user_id), user_id)
                    random_choice.append(get_random_user_data)
                    # пердаем в функцию которая заполняет таблицу search, список случайных пользователей
                    #fill_user_search_table([get_random_user_data], user_id)
                    # если id из списка random_choice не входит в список list_chosen
                    if random_choice[0]['id'] not in list_chosen:
                        # выводим сообщение пользователю результата поиска
                        write_msg(user_id, {random_choice[0]['first_name'] + ' ' + random_choice[0]['last_name']}, None)
                        write_msg(user_id, f"Ссылка на профиль:{random_choice[0]['vk_link']}", None)
                        photos_list = get_photos_list(sort_by_likes(get_photo(random_choice[0]['id'])))
                        write_msg(user_id, None, f"{','.join(photos_list)}")
                        write_msg(user_id, f"Занести пользователя в список избранных? да/нет", None)
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
                            write_msg(user_id, f"Кандидат занесен в черный список", None)
                            # добавляем кандидата в таблицу black_list
                            # добавляем кандидата в список избранных
                            list_chosen.append(random_choice[0]['id'])
                        fill_status_field(random_choice[0]['id'], status)
                        write_msg(user_id,
                                  f"Продолжить поиск? (да/нет)\n"
                                  f"Либо введите 'показать избранных' для вывода списка избранных."
                                  , None)
                    else:
                        continue

                elif request == 'показать избранных':
                    # выводим сообщение пользователю из таблици favorites
                    #write_msg(user_id, f"{check_db_favorites(user_id)}", None)
                    write_msg(user_id, f"Продолжить поиск? да/нет", None)
                elif request in ['пока', 'нет']:
                    write_msg(user_id, "Спасибо за использование сервиса. Всего доброго!", None)
                    break
                else:
                    write_msg(user_id, "Не поняла вашего ответа...", None)

if __name__ == '__main__':
    main()
