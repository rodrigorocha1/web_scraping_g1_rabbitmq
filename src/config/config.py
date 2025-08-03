from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    URL_API = os.environ['URL_API']
    USER_API = os.environ['USER_API']
    SENHA_API = os.environ['SENHA_API']
    CONTENT_TYPE = 'application/json'