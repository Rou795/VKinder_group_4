import datetime
from db_files.models import Base, User, FoundUser, BlackList, Favorite
from db_files.configdb import session, vk_url_base, engine


def fill_user_table(user_data: dict) -> None:
    """
    Функция для заполнения данных о пользователе в таблицу Users
    """
    user = User(user_id=user_data['id'], user_name=user_data['first_name'],
                user_surname=user_data['last_name'], gender=user_data['sex'],
                city=user_data.get('city').get('title'), link=vk_url_base + user_data['domain'],
                user_age=user_data['age'])

    session.add(user)
    session.commit()


def take_from_users(user_id: int) -> dict:
    """
    Функция для получения данных о пользователях из БД
    """
    user = session.query(User).get(user_id)
    user_data = {'id': user_id, 'first_name': user.user_name,
                 'last_name': user.user_surname, 'vk_link': user.link,
                 'age': user.user_age}
    return user_data


def fill_found_user_table(users_founded: list, user_main: int) -> None:
    """
    Функция заполнения таблицы FoundUsers
    """
    today = datetime.datetime.today()
    for user in users_founded:
        age = today.year - user['bdate'].year
        data = session.query(FoundUser).get(user['id'])
        if data is None:
            try:
                user_data = FoundUser(fnd_user_id=user['id'], user_name=user['first_name'],
                                      user_surname=user['last_name'],
                                      gender=user['sex'], city=user.get('city').get('title'),
                                      link=vk_url_base + user['domain'], user_age=age,
                                      user_id=user_main)
            except TypeError as ex:
                user_data = FoundUser(fnd_user_id=user['id'], user_name=user['first_name'],
                                      user_surname=user['last_name'],
                                      gender=user['sex'], city='UKWN',
                                      link=vk_url_base + user['domain'], user_age=age,
                                      user_id=user_main)
            session.add(user_data)
    session.commit()


def fill_favorite(random_choice: dict, user_id: str) -> None:
    """
    Функция заполнения таблицы Favorite
    """
    data = session.query(Favorite).filter(user_id == user_id).all()
    if data:
        for row in data:
            if row.fnd_user_id == random_choice['id']:
                return None
    data = Favorite(fnd_user_id=random_choice['id'], user_id=user_id, user_name=random_choice['first_name'],
                    user_surname=random_choice['last_name'],
                    link=random_choice['vk_link']
                    )
    session.add(data)
    session.commit()


def del_from_favorite(user_id: int, fnd_user_id: int) -> None:
    """
    Функция для удаления людей из списка избранных
    """
    del_user = session.query(Favorite).filter(Favorite.user_id == user_id,
                                              Favorite.fnd_user_id == fnd_user_id)
    session.delete(del_user)
    session.commit()


def del_from_black_list(user_id: int, fnd_user_id: int) -> None:
    """
        Функция для удаления людей из черного списка
    """
    del_user = session.query(BlackList).filter(BlackList.user_id == user_id,
                                               BlackList.fnd_user_id == fnd_user_id)
    session.delete(del_user)
    session.commit()


def take_from_bd(user_id: int) -> list:
    """
    Функция выгрузки людей, найденных ранее из БД (таблица FoundUsers)
    """
    users = []
    data = session.query(FoundUser).filter(FoundUser.user_id == user_id).all()
    black_marker = session.query(BlackList).filter(BlackList.user_id == user_id).all()
    favorite_marker = session.query(Favorite).filter(Favorite.user_id == user_id).all()
    black_list = [el.fnd_user_id for el in black_marker]
    favorite_list = [el.fnd_user_id for el in favorite_marker]
    cancel_list = black_list + favorite_list
    for row in data:
        if row.show_marker is False:
            if row.fnd_user_id not in cancel_list:
                users.append({'id': row.fnd_user_id, 'first_name': row.user_name,
                              'last_name': row.user_surname, 'vk_link': row.link})
    return users


def show_status_maker(user_id: int, showed_peoples: list) -> None:
    """
    Функция для выставления статуса просмотренно в таблице FoundUsers
    """
    for people in showed_peoples:
        row = session.query(FoundUser).filter(FoundUser.fnd_user_id == people, FoundUser.user_id == user_id).all()
        row[0].show_marker = True
        session.add(row[0])
    session.commit()


def fill_black_list(random_user: dict, user_id: int) -> None:
    """
    Функция для заполнения таблицы BlackList
    """
    user_black_list = session.query(BlackList).filter(BlackList.user_id == user_id).all()
    if user_black_list:
        for user in user_black_list:
            if user.fnd_user_id == random_user:
                return None
        user_data = BlackList(fnd_user_id=random_user['id'], user_id=user_id)
        session.add(user_data)
    else:
        user_data = BlackList(fnd_user_id=random_user['id'], user_id=user_id)
        session.add(user_data)
    session.commit()


def check_db_favorites(user_id: str) -> list:
    """
    Функция для выгрузки списка избранных из базы
    """
    db_favorites = session.query(Favorite).filter(Favorite.user_id == user_id).all()
    all_users = []
    if db_favorites:
        for item in db_favorites:
            all_users.append((item.fnd_user_id, 'id:' + str(item.fnd_user_id), item.user_name + ' ' + item.user_surname,
                              item.link + ' '))
        return all_users


def check_user(user_id: int) -> bool:
    """
    Функция для проверки существования пользователя в базе
    """
    user = session.query(User).get(user_id)
    if user is None:
        return True
    else:
        return False


def create_tables(engine) -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    create_tables(engine)
