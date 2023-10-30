import os
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# DB settings
DB_NAME: str = os.getenv('NAME_DB')
user: str = os.getenv('USER')
password: str = os.getenv('PASSWORD')
DSN: str = f'postgresql://postgres:{password}@localhost:5432/{DB_NAME}'
echo: bool = False

# переменные model.py
engine = sa.create_engine(url=DSN, echo=echo)
vk_url_base = 'https://vk.com/'
Session = sessionmaker(bind=engine)
session = Session()

