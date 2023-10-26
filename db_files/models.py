import os
import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker
#from configdb import DSN, echo, engine, vk_url_base, Session, session
from db_files.configdb import DSN, echo, engine, vk_url_base, Session, session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    user_name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    user_surname: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    gender: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    city: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    link: so.Mapped[str] = so.mapped_column(sa.Text, unique=True, nullable=False)
    user_age: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)

    user_found_user: so.Mapped["FoundUser"] = relationship(back_populates='found_user_user')
    user_black_list: so.Mapped["BlackList"] = relationship(back_populates='black_list_user')
    user_favorite: so.Mapped["Favorite"] = relationship(back_populates='favorite_user')


class FoundUser(Base):
    __tablename__ = 'found_user'

    fnd_user_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    user_name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    user_surname: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    gender: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    city: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    link: so.Mapped[str] = so.mapped_column(sa.Text, unique=True, nullable=False)
    user_age: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, ForeignKey('user.user_id'))

    found_user_user: so.Mapped["User"] = relationship(back_populates='user_found_user')
    found_user_black_list: so.Mapped["BlackList"] = relationship(back_populates='black_list_found_user')
    found_user_favorite: so.Mapped["Favorite"] = relationship(back_populates='favorite_found_user')


class BlackList(Base):
    __tablename__ = 'black_list'

    fnd_user_id: so.Mapped[int] = so.mapped_column(sa.Integer, ForeignKey('found_user.fnd_user_id'), unique=True,
                                                   primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, ForeignKey('user.user_id'))

    black_list_user: so.Mapped["User"] = relationship(back_populates='user_black_list')
    black_list_found_user: so.Mapped["FoundUser"] = relationship(back_populates='found_user_black_list')


class Favorite(Base):
    __tablename__ = 'favorite'

    fnd_user_id: so.Mapped[int] = so.mapped_column(sa.Integer, ForeignKey('found_user.fnd_user_id'), unique=True,
                                                   primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, ForeignKey('user.user_id'))
    user_name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    user_surname: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    link: so.Mapped[str] = so.mapped_column(sa.Text, unique=True, nullable=False)

    favorite_user: so.Mapped["User"] = relationship(back_populates='user_favorite')
    favorite_found_user: so.Mapped["FoundUser"] = relationship(back_populates='found_user_favorite')
   


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

# def fill_white_list(random_choice, user_id):
#     for item in random_choice:
#         data = session.query(Favorite).filter_by(usser_id=item['id']).scalar()
#         if not data:
#             user_data = Favorite(fnd_user_id=item['id'], first_name=item['first_name'], last_name=item['last_name'],
#                                             vk_link=item['vk_link']
#                                             )
#         session.add(user_data)
#     return session.commit()

def fill_black_list(random_choice, user_id):
    for item in random_choice:
        data = session.query(BlackList).filter_by(user_id=item['id']).scalar()
        if not data:
            user_data = BlackList(fnd_user_id=item['id'], user_id=user_id)
        session.add(user_data)
    return session.commit()

# def check_db_favorites(user_id):
#     db_favorites = session.query(Favorite).order_by(Favorite.user_id).all()
#     all_users = []
#     if db_favorites:
#         for item in db_favorites:
#             all_users.append([item.user_id, 'id:'+str(item.id), item.first_name+' '+item.last_name, item.vk_link+' '])
#         return all_users
#     write_msg(user_id, 'Ошибка', None)
#     return False

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
   
