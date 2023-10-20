from random import randrange
from vk_bot import VkBot
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

with open('token.txt') as f:
    token = f.read()
#token = input('Token: ')

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            print('New message:')
            print(f'For me by: {event.user_id}', end='')

            bot = VkBot(event.user_id)
            write_msg(event.user_id, bot.new_message(event.text))
            print('Text: ', event.text)
