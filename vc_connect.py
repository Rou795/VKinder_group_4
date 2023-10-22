import requests

api_base_url_vk = 'https://api.vk.com/method/'
with open('token.txt') as f:
    token = f.read()


#метод для запроса информации о пользователе
def get_info_user(users_id: list) -> list:
    url = api_base_url_vk + 'users.get'
    data = []
    params = {'access_token': token, 'user_id': users_id, 'fields': ['bdate, sex, city, domain'], 'v': '5.131'}
    response = requests.get(url=url, params=params)
    if 200 <= response.status_code < 300:
        users_data = response.json()['response']
        for user in users_data:
            data.append({'id': user['id'], 'first_name': user['first_name'],
                         'last_name': user['last_name'], 'sex': user['sex'],
                         'city': user['city']['title'], 'domain': user['domain'],
                         'bdate': user['bdate']})
        return data
    else:
        print(f'Bad connection: {response.status_code}')


users = get_info_user(['36356648'])
print(users)