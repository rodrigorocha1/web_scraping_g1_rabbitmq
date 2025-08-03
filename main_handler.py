from src.context.pipeline_context import PipelineContext
from src.handler_cadeia_pipeline.obternoticiag1handler import ObterUrlG1Handler
from src.handler_cadeia_pipeline.obterrsshandler import ObterRSSHandler
from src.handler_cadeia_pipeline.processar_noticia_handler import ProcessarNoticiaHandler
from src.handler_cadeia_pipeline.verificar_noticiag1_cadastadra_handler import VerificarNoticiaCadastradaHandler
from src.servicos.extracao.webscrapingbs4g1rss import WebScrapingBs4G1Rss
from src.servicos.extracao.webscrapingsiteg1 import WebScrapingG1
from src.servicos.manipulador.arquivo_docx import ArquivoDOCX
from src.servicos.s_api.noticia_api import NoticiaAPI
from src.handler_cadeia_pipeline.checarconexaohandler import ChecarConexaoHandler
from bs4 import BeautifulSoup
from typing import Generator, Dict, Any
from src.models.noticia import Noticia

rss_service = WebScrapingBs4G1Rss(url="https://g1.globo.com/rss/g1/sp/ribeirao-preto-franca")
g1_service = WebScrapingG1(url=None, parse="html.parser")
arquivo = ArquivoDOCX()
noticia_api = NoticiaAPI()

contexto = PipelineContext[Generator[Dict[str, Any], None, None]]()

p1 = ChecarConexaoHandler(api_noticia=noticia_api)

p2 = ObterRSSHandler[BeautifulSoup, Generator[Dict[str, Any], None, None]](
    servico_webscraping=rss_service
)
p3 = ObterUrlG1Handler[BeautifulSoup, Noticia](
    web_scraping_g1=g1_service
)
p4 = VerificarNoticiaCadastradaHandler(
    api_noticia=noticia_api
)

p5 = ProcessarNoticiaHandler(
    api_noticia=NoticiaAPI(),
    arquivo=ArquivoDOCX()
)

p1.set_next(p2) \
    .set_next(p3) \
    .set_next(p4) \
    .set_next(p5)



p1.handle(contexto)
