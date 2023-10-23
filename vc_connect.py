from datetime import datetime
import vk_api
import requests
from datetime import date
import time

api_base_url_vk = 'https://api.vk.com/method/'
token_group = 'vk1.a.ggLarpWkBcLDihQVCdatjKi3UcI6PAJlg55_63gWFTa3ICL5eOdxXhTYK4TZDAG-QUx2GbjaFNoH5H4Z9YlWlxNqcLGOizmhWLtCGna-07mpIbKOZXi1VJ70c1beJqrJOrZuynItxD9cj6LPSykg-FrbzEfzua7bIHiFuF2aOokAnBJBvUTMq-D0MGxStIFJjJ6O0O3hQ7QR8jL1HXAPSQ'
token_user = 'vk1.a.rGVB58pIqVdqgHse3aKuzRSiBSQ6oPbGQx1F4F05KE6smrEH0SGoWfsKxm4mIgJood4OfxF5zDdVAC7P2znufYdimMJpWdotOPQ6yBgtE_Oc7Vly1k3_JHoaeODoOsCfzQ3lW2wSeA8v14yiOvhnIeD9OLZYuTaKpZT-17fujVjflxOZE8Ew_bq86p0R_3m7'

vk = vk_api.VkApi(token=token_group)
# токен пользователя
vk2 = vk_api.VkApi(token=token_user)
user_id = '36356648'
requested_fields = ['first_name', 'last_name', 'bdate', 'sex', 'city', 'domain']
required_info = requested_fields.copy()
required_info.extend(['domain', 'age', 'id'])
response = vk.method('users.get', {'user_id': user_id,
                                   'v': 5.154,
                                   'fields': ','.join(requested_fields)})


user_data = {}
for key, value in response[0].items():
    if key in required_info:
        if key == 'bdate':
            user_data[key] = datetime.strptime(value, '%d.%m.%Y').date()
        else:
            user_data[key] = value

today = datetime.today()
user_data['age'] = today.year - user_data['bdate'].year

#метод для запроса информации о пользователе
resp = vk2.method('users.search', {
                                'fields': ','.join(requested_fields),
                                'age_from': user_data['age'] - 3,
                                'age_to': user_data['age'] + 3,
                                'city': user_data['city']['id'],
                                'sex': 3 - user_data['sex'],
                                'relation': 6,
                                'has_photo': 1,
                                'count': 400,
                                'v': 5.154})

count = resp['count']
users = resp['items']
users_data = []

for user in users:
    user_template = {}
    for key, value in user.items():
        if key in required_info:
            if key == 'bdate':
                if value.count('.') == 2:
                    user_template[key] = datetime.strptime(value, '%d.%m.%Y').date()
                elif value.count('.') == 1:
                    user_template[key] = datetime.strptime(value, '%d.%m').date()
                else:
                    user_template[key] = value
            else:
                user_template[key] = value
    users_data.append(user_template.copy())
    user_template.clear()
print(users_data)
print(len(users_data))
print(count)

date = datetime.strptime('20.10', '%d.%m')
print(date)
print(type(date.year))