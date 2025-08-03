import logging
from typing import Optional, TypeVar
from abc import abstractmethod, ABC
import requests
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from bs4 import BeautifulSoup
from src.tratamento.tratamento import Tratamento
from requests.exceptions import HTTPError, ConnectionError, ConnectTimeout, ReadTimeout, TooManyRedirects, \
    RequestException

from src.utils.db_handler import DBHandler

U = TypeVar('U')

FORMATO = '%(asctime)s %(filename)s %(funcName)s'
db_handler = DBHandler(nome_pacote='WebScrapingBs4base', formato_log=FORMATO, debug=logging.DEBUG)

logger = db_handler.loger


class WebScrapingBs4base(IWebScapingBase[BeautifulSoup, U], ABC):

    def __init__(self, url: Optional[str], parse: str):
        """
        Construtor da classe
        :param url: url de conexão
        :type url: string
        :param parse: tipo de parse do bs4
        type parse: str
        """

        self._parse = parse
        self._url = url
        self._tratamento = Tratamento()

    @property
    def url(self) -> str:
        """
        Método de validação
        :return: url validada
        :rtype: str
        """
        if self._url is None:
            raise ValueError("URL não pode ser None")
        return self._url

    @url.setter
    def url(self, nova_url: str) -> None:
        """
        url do web scraping
        :param nova_url: url da extração
        :type nova_url: str
        :return:  Sem retorno
        :rtype: None
        """
        self._url = nova_url

    def abrir_conexao(self) -> Optional[BeautifulSoup]:
        """
        Método para abrir a conexão do bs4
        :return: objeto do BeautifulSoup
        :rtype: BeautifulSoup
        """
        try:
            if self._url is None:
                raise ValueError("URL não pode ser None")
            logger.info(
                f'Conectando na URL ',
                extra={'url': self._url}
            )
            response = requests.get(url=self._url)
            response.raise_for_status()
            conteudo_response = response.content
            logger.info(
                f'Sucesso ao conectar ',
                extra={
                    'url': self._url,
                    'status_code': response.status_code,
                    'requisicao' : response.text
                }
            )
            try:
                soup = BeautifulSoup(conteudo_response, self._parse)
                return soup

            except Exception as e:
                logger.error(
                    msg=f'Erro inesperado {e}',
                    extra={
                        'url': self._url,
                        'status_code': response.status_code
                    }
                )
                return None

        except HTTPError as http_err:
            logger.error(
                msg=f"Erro HTTP  - Pipeline fechado",
                extra={
                    'url': self._url,
                    'status_code': response.status_code,
                    'mensagem_de_execao_tecnica': http_err

                }
            )
            return None
        except ConnectionError:
            logger.error(
                msg=f'Erro de conexão - Pipeline fechado',
                extra={
                    'url': self._url,
                    'status_code': response.status_code
                }
            )
            return None
        except ConnectTimeout:
            logger.error(
                msg=f'Tempo de conexão excedido url - Pipeline fechado ',
                extra={
                    'url': self._url,
                    'status_code': response.status_code
                }
            )
            return None
        except ReadTimeout:
            logging.error(
                msg=f"Tempo de leitura excedido url - Pipeline fechado",
                extra={
                    'status_code': response.status_code,
                    'url': self._url
                }
            )
            return None
        except TooManyRedirects:
            logging.error(
                msg="Redirecionamentos em excesso detectados. url {self._url} - Pipeline fechado",
                extra={
                    'url': self._url,
                    'status_code': response.status_code
                }
            )
            return None
        except RequestException as req_err:
            logging.error(
                msg=f"Erro de requisição: url - Pipeline fechado",
                extra={
                    'url': self._url,
                    'status_code': response.status_code,
                    'mensagem_de_execao_tecnica': req_err
                }
            )
            return None
        except Exception as e:
            logging.error(
                msg=f"Erro inesperado: url  - Pipeline fechado",
                extra={
                    'url': self._url,
                    'status_code': response.status_code,
                    'mensagem_de_execao_tecnica': e
                }
            )
            return None

    @abstractmethod
    def obter_dados(self, dados: BeautifulSoup) -> U:
        """
        Método para obter os dados da extração
        :param dados: objeto BS4
        :type dados: BeautifulSoup
        :return: dados obtidos da Noticia
        :rtype: BeautifulSoup
        """
        pass
