import os
import vk_api
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll

load_dotenv()
# token group
token_group = os.getenv('TOKENAPI')
# token user
token_user = os.getenv('TOKENUSER')

# DB settings
DB_NAME: str = 'vkinder'
user: str = 'postgres'
password: str = '1209'
DSN: str = f'postgresql://postgres:{password}@localhost:5432/{DB_NAME}'
echo: bool = False
#
engine = sa.create_engine(url=DSN, echo=echo)
vk_url_base = 'https://vk.com/'
Session = sessionmaker(bind=engine)
session = Session()

# Ссылки на токены
# токен группы
vk = vk_api.VkApi(token=token_group)
# токен пользователя
vk2 = vk_api.VkApi(token=token_user)
longpoll = VkLongPoll(vk)

# переменные поиска
requested_fields = ['first_name', 'last_name', 'bdate', 'sex', 'city', 'domain']