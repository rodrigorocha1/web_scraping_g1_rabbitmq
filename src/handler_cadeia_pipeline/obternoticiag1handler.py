from src.context.pipeline_context import PipelineContext
from src.handler_cadeia_pipeline.handler import Handler
from typing import TypeVar, Generic, Generator

from src.models.noticia import Noticia
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase

SWB = TypeVar('SWB')
RTN = TypeVar('RTN')


class ObterUrlG1Handler(Handler, Generic[SWB, RTN]):
    def __init__(self, web_scraping_g1: IWebScapingBase[SWB, RTN]):
        super().__init__()
        self.__servico_web_scraping_g1 = web_scraping_g1

    def executar_processo(self, context: PipelineContext) -> bool:
        """
        Método que vai representar o processo,ex: = Conectar url rss
        :param context: contexto do pipeline, váriaveis que seão passadas
        :type context: context.pipeline_context.PipelineContext
        :return: Verdadeiro se o processo for executado com sucesso Falso caso contrário
        :rtype: bool
        """
        dados_g1 = context.rss
        if isinstance(dados_g1, Generator):
            for dado in dados_g1:
                if isinstance(dado, dict) and dado['url_rss'] is not None:
                    self.__servico_web_scraping_g1.url = dado['url_rss']
                    dado_g1 = self.__servico_web_scraping_g1.abrir_conexao()
                    if dado_g1:
                        noticia = self.__servico_web_scraping_g1.obter_dados(dados=dado_g1)
                        if isinstance(noticia, Noticia):
                            context.noticia_g1.append((dado['url_rss'] ,noticia))
            return True
        return False
