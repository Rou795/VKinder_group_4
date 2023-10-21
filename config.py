import os
from dotenv import load_dotenv

load_dotenv()
# token group
token_group = os.getenv('TOKENAPI')
# token user
token_user = os.getenv('TOKENUSER')

