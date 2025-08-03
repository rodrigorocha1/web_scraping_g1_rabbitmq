from abc import ABC, abstractmethod
from typing import Optional

from src.context.pipeline_context import PipelineContext
from src.utils.db_handler import DBHandler
import logging

FORMATO = '%(asctime)s %(filename)s %(funcName)s %(module)s  - %(message)s'
db_handler = DBHandler(nome_pacote='Handler', formato_log=FORMATO, debug=logging.DEBUG)

logger = db_handler.loger


class Handler(ABC):

    def __init__(self) -> None:
        self._next_handler: Optional['Handler'] = None

    def set_next(self, hander: "Handler") -> "Handler":
        """
        Metodo para executar a cadeia
        :param hander: o Tipo de cadia
        :type hander: Handler
        :return: A Cadeia Ex: Conectar na api, acessar site
        :rtype: Handler
        """
        self._next_handler = hander
        return hander

    def handle(self, context: PipelineContext) -> None:
        """
        Método que vai representar o fluxo do etl
        :param context: Recebe os contexto do pipeline
        :type context: PipelineContext
        :return: Nada
        :rtype: None
        """
        logger.info(f'{self.__class__.__name__} -> Iniciando web scraping')
        if self.executar_processo(context):
            logger.info(f'{self.__class__.__name__} -> Sucesso ao executar')
            if self._next_handler:
                self._next_handler.handle(context)
            else:
                logger.info(f'{self.__class__.__name__} ->  Último handler da cadeia')
        else:
            logger.warning(f'{self.__class__.__name__} -> Falha, pipeline interrompido')

    @abstractmethod
    def executar_processo(self, context: PipelineContext) -> bool:
        """
        Método que vai representar o processo,ex: =Checar conexão na api
        :param context: contexto do pipeline, váriaveis que seão passadas
        :type context: PipelineContext
        :return: Verdadeiro se o processo for executado com sucesso Falso caso contrário
        :rtype: bool
        """
        pass
