from typing import Generator, Dict, Any

import pika
import sys
import time
from bs4 import BeautifulSoup
from pika.spec import BasicProperties
from pika.spec import Basic
from pika.adapters.blocking_connection import BlockingChannel
from src.models.noticia import Noticia
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from src.servicos.extracao.webscrapingsiteg1 import WebScrapingG1
from src.servicos.manipulador.arquivo import Arquivo
from src.servicos.manipulador.arquivo_docx import ArquivoDOCX

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Noticia


class NoticiaTrabalhador:

    def __init__(self, nome_fila: str, servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador],
                 arquivo: Arquivo):
        self.__credenciais = pika.PlainCredentials('rodrigo', '123456')
        self.__parametros_conexao = pika.ConnectionParameters(
            host='172.30.0.10',
            port=5672,
            virtual_host='/',
            credentials=self.__credenciais
        )
        self.__conexao = pika.BlockingConnection(self.__parametros_conexao)
        self.__servico_web_scraping = servico_web_scraping
        self.__arquivo = arquivo
        self.__nome_fila = nome_fila

    def callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        url = body.decode()
        print('=' * 100)
        self.__servico_web_scraping.url = url
        dados = self.__servico_web_scraping.abrir_conexao()
        noticia = self.__servico_web_scraping.obter_dados(dados=dados)
        if noticia.texto:
            print(noticia.texto)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def rodar(self):
        canal = self.__conexao.channel()
        try:

            canal.queue_declare(queue=self.__nome_fila, durable=True)
            canal.basic_qos(prefetch_count=1)
            print('consume')
            canal.basic_consume(
                queue=self.__nome_fila,
                on_message_callback=self.callback
            )
            canal.start_consuming()
        except KeyboardInterrupt:
            canal.stop_consuming()


if __name__ == '__main__':
    nome_fila = sys.argv[1]
    print(nome_fila)
    servico_web_scraping = WebScrapingG1(url=None, parse="html.parser")
    arquivo = ArquivoDOCX()
    notica_worker = NoticiaTrabalhador(
        nome_fila=nome_fila,
        servico_web_scraping=servico_web_scraping,
        arquivo=arquivo
    )
    notica_worker.rodar()
