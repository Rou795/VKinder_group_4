from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy_utils import database_exists, create_database
from database import create_tables, drop_tables, User, User_search_data, White_list, Black_list
from sqlalchemy.exc import IntegrityError, InvalidRequestError, PendingRollbackError


url_object = URL.create(
    'postgresql',
    username='postgres',
    password='BorgH8417',
    host='localhost',
    database='VKinderDB',
)


# Creating engine
# Создание движка
engine = create_engine(url_object)

# Creating database
# Создание базы данных
if not database_exists(engine.url):
    create_database(engine.url)

# Droping existing tables
# Удаление существующих таблиц
drop_tables(engine)
#Creating tables
# Создание таблиц
create_tables(engine)

Session = sessionmaker(bind=engine)

session = Session()

def fill_user_table(user_data):
    """
    Filling user table
    Заполняет таблицу user
    """
    if user_data:
        for item in user_data:
            user_record = session.query(User).filter_by(id=item['id']).scalar()
            if not user_record:
                user_record = User(id=item['id'])
            session.add(user_record)
            session.commit()
        return True
    write_msg(user_data['id'], 'Ошибка', None)
    return False

def fill_user_search_table(users_data, user_id):
    """
    Filling search table
    заполняет таблицу search
    """
    try:
        for item in users_data:
            users_record = session.query(User_search_data).filter_by(id=item['id']).scalar()
            if not users_record:
                users_record = User_search_data(id=item['id'])
            session.add(users_record)
            session.commit()
        return True
    except (IntegrityError, InvalidRequestError, PendingRollbackError, TypeError):
        session.rollback()
        write_msg(user_id, 'Ошибка', None)
        return False

def fill_white_list(random_choice):
    """
    Filling white_list table
    заполняет таблицу white_list
    """
    for item in random_choice:
        random_user_record = session.query(White_list).filter_by(id=item['id']).scalar()
        if not random_user_record:
            random_user_record = White_list(id=item['id'], first_name=item['first_name'], last_name=item['last_name'],
                                            vk_link=item['vk_link']
                                            )
        session.add(random_user_record)
    return session.commit()

def fill_black_list(random_choice):
    """
    Filling black_list table
    Заполняет таблицу black_list
    """
    for item in random_choice:
        random_user_record = session.query(Black_list).filter_by(id=item['id']).scalar()
        if not random_user_record:
            random_user_record = Black_list(id=item['id'])
        session.add(random_user_record)
    return session.commit()

def check_db_favorites(user_id):
    """
    Getting list of favorites
    Получяет список из таблицы favorites
    """
    db_favorites = session.query(White_list).order_by(White_list.user_id).all()
    all_users = []
    if db_favorites:
        for item in db_favorites:
            all_users.append([item.user_id, 'id:'+str(item.id), item.first_name+' '+item.last_name, item.vk_link+' '])
        return all_users
    write_msg(user_id, 'Ошибка', None)
    return False