
import sqlalchemy as sa
import sqlalchemy.orm as so

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from db_files.configdb import engine


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

def create_tables(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    create_tables(engine)
   
