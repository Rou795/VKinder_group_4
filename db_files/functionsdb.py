import datetime

from db_files.models import Base, User, FoundUser, BlackList, Favorite
from db_files.configdb import Session, session, vk_url_base, DSN, echo, engine


def fill_user_table(user_data: dict) -> None:
    today = datetime.datetime.today()
    users = user_data['id']
    #age = today.year - user_data['bdate'].year 
    data = session.query(User).get(users)
    if data is None:
        user = User(user_id=user_data['id'], user_name=user_data['first_name'],
                    user_surname=user_data['last_name'], gender=user_data['sex'],
                    city=user_data['city'], link=vk_url_base + user_data['domain'],
                    user_age=user_data['age'])

        session.add(user)
        session.commit()

def fill_found_user_table(users_founded: list, user_main: int) -> None:
    today = datetime.datetime.today()
    for user in users_founded:
        age = today.year - user['bdate'].year
        data = session.query(FoundUser).get(user['id'])
        if data is None:
            try:
                user_data = FoundUser(fnd_user_id=user['id'], user_name=user['first_name'],
                                      user_surname=user['last_name'],
                                      gender=user['sex'], city=user.get('city')['title'],
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

def fill_white_list(random_choice, user_id):
    for item in random_choice:
        data = session.query(Favorite).filter_by(fnd_user_id=item['user_id']).scalar()
        if not data:
            data = Favorite(fnd_user_id=item['id'], user_id=item['user_id'], user_name=item['first_name'], user_surname=item['last_name'],
                                            link=item['vk_link']
                                            )
        session.add(data)
    return session.commit()

def fill_black_list(random_choice, user_id):
    for item in random_choice:
        data = session.query(BlackList).filter_by(user_id=item['id']).scalar()
        if not data:
            user_data = BlackList(fnd_user_id=item['id'], user_id=user_id)
        session.add(user_data)
    return session.commit()

def check_db_favorites(user_id):
    db_favorites = session.query(Favorite).order_by(Favorite.user_id).all()
    all_users = []
    if db_favorites:
        for item in db_favorites:
            all_users.append([item.user_id, 'id:'+str(item.fnd_user_id), item.user_name+' '+item.user_surname, item.link+' '])
        return all_users

def fill_status_field(user_id: int, status: int) -> None:
    user_found = session.query(FoundUser).get(user_id)
    user_found.status = status
    session.add(user_found)
    session.commit()

def create_tables(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    create_tables(engine)
   
