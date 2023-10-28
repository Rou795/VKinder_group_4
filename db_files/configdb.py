import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

# DB settings
DB_NAME: str = 'vkinder'
user: str = 'postgres'
password: str = '6802425'
DSN: str = f'postgresql://postgres:{password}@localhost:5432/{DB_NAME}'
echo: bool = False

# переменные model.py
engine = sa.create_engine(url=DSN, echo=echo)
vk_url_base = 'https://vk.com/'
Session = sessionmaker(bind=engine)
session = Session()
