from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    URL_FILA = os.environ['URL_FILA']
    USR_FILA = os.environ['USR_FILA']
    PORTA_FILA = os.environ['PORTA_FILA']
    PASSWD_FILA = os.environ['PASSWD_FILA']
