import hashlib
from src.context.pipeline_context import PipelineContext
from src.handler_cadeia_pipeline.handler import Handler
from src.servicos.s_api.inoticia_api import INoticiaApi
from src.utils.db_handler import DBHandler
import logging

FORMATO = '%(asctime)s %(filename)s %(funcName)s - %(message)s'
db_handler = DBHandler(nome_pacote='VerificarNoticiaCadastradaHandler', formato_log=FORMATO, debug=logging.DEBUG)

logger = db_handler.loger


class VerificarNoticiaCadastradaHandler(Handler):
    def __init__(self, api_noticia: INoticiaApi):
        super().__init__()
        self.__api_noticia = api_noticia

    def executar_processo(self, context: PipelineContext) -> bool:
        """
        Método que vai representar o processo,ex: Verificar noticia cadastrada
        :param context: contexto do pipeline, váriaveis que seão passadas
        :type context: PipelineContext
        :return: Verdadeiro se o processo for executado com sucesso Falso caso contrário
        :rtype: bool
        """
        try:
            for url in context.noticia_g1:
                if url[1].texto:


                    id_noticia = hashlib.md5(url[0].encode('utf-8')).hexdigest()
                    id_noticia_api = self.__api_noticia.consultar_dados_id(id_noticia=id_noticia)

                    if not id_noticia_api:
                        context.noticia_g1_nao_cadastrada.append(url)
                    else:
                        logger.warning(f'log: Notícia já cadastrada -> Tílulo da noticia: {url[1].titulo}', extra={
                        'url': url[0]
                    })
                else:
                    logger.debug(f'A url não apesenta texto da noticia', extra={
                        'url': url[0]
                    })

            return True


        except Exception:
            return False
