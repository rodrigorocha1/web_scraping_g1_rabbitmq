from src.context.pipeline_context import PipelineContext
from src.handler_cadeia_pipeline.handler import Handler
from typing import Generic, TypeVar
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase

SWB = TypeVar('SWB')
RTN = TypeVar('RTN')





class ObterRSSHandler(Handler, Generic[SWB, RTN]):

    def __init__(self, servico_webscraping: IWebScapingBase[SWB, RTN]):

        super().__init__()
        self._servico_web_scraping_rss = servico_webscraping

    def executar_processo(self, context: PipelineContext) -> bool:
        dados = self._servico_web_scraping_rss.abrir_conexao()
        if dados:
            rss_result = self._servico_web_scraping_rss.obter_dados(dados)
            context.rss = rss_result

            return True
        return False
