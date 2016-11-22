import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

if os.environ.get('HEROKU'):
    from .production import *
else:
    from .base import *
