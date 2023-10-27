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

# Ссылки на токены
# токен группы
vk = vk_api.VkApi(token=token_group)
# токен пользователя
vk2 = vk_api.VkApi(token=token_user)
longpoll = VkLongPoll(vk)

