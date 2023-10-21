import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from config import DSN, echo

engine = sa.create_engine(url=DSN, echo=echo)


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


class FoundUser(Base):
    __tablename__ = 'found_user'

    fnd_user_id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    user_name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    user_surname: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    gender: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    city: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    link: so.Mapped[str] = so.mapped_column(sa.Text, unique=True, nullable=False)
    user_age: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    status: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, ForeignKey('user.user_id'))

    found_user_user: so.Mapped["User"] = relationship(back_populates='user_found_user')


def create_tables(engine):
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    create_tables(engine)
