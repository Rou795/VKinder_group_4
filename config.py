import os
from dotenv import load_dotenv

load_dotenv()
# token group
token_group = os.getenv('TOKENAPI')
# token user
token_user = os.getenv('TOKENUSER')

# DB settings
DB_NAME: str = 'vkinder'
user: str = 'postgres'
password: str = 'Tdutybq2020'

DSN: str = f'postgresql://postgres:{password}@localhost:5432/{DB_NAME}'
echo: bool = False