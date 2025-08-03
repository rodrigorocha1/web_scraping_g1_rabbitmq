from src.handler_cadeia_pipeline.handler import Handler
from src.servicos.s_api.inoticia_api import INoticiaApi
from src.context.pipeline_context import PipelineContext
from src.utils.db_handler import DBHandler
import logging

FORMATO = '%(asctime)s %(filename)s %(funcName)s  - %(message)s'
db_handler = DBHandler(nome_pacote='ChecarConexaoHandler', formato_log=FORMATO, debug=logging.DEBUG)

logger = db_handler.loger


class ChecarConexaoHandler(Handler):
    def __init__(self, api_noticia: INoticiaApi):
        super().__init__()
        self._api_noticia = api_noticia

    def executar_processo(self, context: PipelineContext) -> bool:
        """
        Método que vai representar o processo,ex: Checar conexão na api
        :param context: contexto do pipeline, váriaveis que seão passadas
        :type context: Union[Dict, context.pipeline_context.PipelineContext]
        :return: Verdadeiro se o processo for execudado com sucesso Falso caso contrário
        :rtype: bool
        """
        conexao = self._api_noticia.checar_conexao()
        if conexao:
            logger.info('Conexão API realizada com sucesso')
            return True
        else:
            logger.error('Falha na conexão na API')
            return False
