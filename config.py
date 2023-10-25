import os
import vk_api
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


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
# переменные model.py
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

# правила бота
rules = [
    f"Вас приветствует бот VKinder!\n"
    f"Бот осуществляет поиск подходящей по критериям пары и заносит в список избранных или "
    f" в черный список по указанию пользователя.\n"
    f"Критерии: город пользователя, возраст в промежутке от -3 лет до +3 лет"
    f" от возраста пользователя.\n"
    f"Чтобы начать поиск нажмите кнопку 'начать поиск'.\n"
    f"Для окончания работы с ботом нажмите кнопку 'пока',"
    f" либо нажмите кнопку 'нет' при вопросе о продолжении поиска."
]
search_rules = ['начать поиск', 'продолжить поиск', 'да']
input_rules = ['привет', 'приветствую', 'hi', 'hello','здарова', 'здравствуйте', 'приветики']
removal_rules = ['пока', 'нет']