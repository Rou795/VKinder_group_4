# DB settings
DB_NAME: str = 'vkinder'
user: str = 'postgres'
password: str = '6802425'

DSN: str = f'postgresql://postgres:{password}@localhost:5432/{DB_NAME}'
echo: bool = False
