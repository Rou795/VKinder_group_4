import os
from dotenv import load_dotenv

load_dotenv()

token_group = os.getenv('TOKENAPI')
token_user = os.getenv('TOKENUSER')