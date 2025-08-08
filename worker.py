from typing import TypeVar, Dict

import pika
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from src.servicos.extracao.webscrapingbs4g1rss import WebScrapingBs4G1Rss

T = TypeVar('T')
U = TypeVar('U')


class ProdutorNoticiaRSS:

    def __init__(self, web_scaping_service: IWebScapingBase[T, U]):
        self.__habit_host = ''
        self.__servico_web_scraping = web_scaping_service
        self.__credenciais = pika.PlainCredentials('rodrigo', '123456')
        self.__parametros_conexao = pika.ConnectionParameters(
            host='172.30.0.10',
            port=5672,  # padrão do RabbitMQ
            virtual_host='/',  # padrão, pode mudar se você configurou diferente
            credentials=self.__credenciais
        )

    def enviar_para_fila(self, nome_fila: str, menssagem):
        conexao = pika.BlockingConnection(self.__parametros_conexao)
        canal = conexao.channel()
        canal.queue_declare(queue=nome_fila, durable=True)
        canal.basic_publish(exchange='', routing_key=nome_fila, body=menssagem)
        conexao.close()

    def processar_rss(self, rss_url: str, nome_fila: str):
        url = self.__servico_web_scraping.url = rss_url
        objeto_conexao = self.__servico_web_scraping.abrir_conexao()
        for dados_rss in self.__servico_web_scraping.obter_dados(dados=objeto_conexao):
            self.enviar_para_fila(nome_fila=nome_fila, menssagem=dados_rss['url_rss'])

    def rodar(self, rss_urls: Dict):
        for nome_fila, rss_url in rss_urls.items():
            self.processar_rss(rss_url=rss_url, nome_fila=nome_fila)
