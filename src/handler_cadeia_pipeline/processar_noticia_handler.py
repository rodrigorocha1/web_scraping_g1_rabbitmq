from src.context.pipeline_context import PipelineContext
from src.handler_cadeia_pipeline.handler import Handler
from src.servicos.manipulador.arquivo import Arquivo

from src.servicos.s_api.inoticia_api import INoticiaApi


class ProcessarNoticiaHandler(Handler):

    def __init__(self, api_noticia: INoticiaApi, arquivo: Arquivo):
        super().__init__()
        self.__api_noticia = api_noticia
        self.__arquivo = arquivo
        self.__diretorio = 'noticia/'

    def executar_processo(self, context: PipelineContext) -> bool:
        """
        Método que vai representar o processo,ex: = Processar arquivo

        :param context: contexto do pipeline, váriaveis que seão passadas
        :type context: PipelineContext
        :return: Verdadeiro se o processo for executado com sucesso Falso caso contrário
        :rtype: bool
        """
        noticias_g1 = context.noticia_g1_nao_cadastrada
        for noticia_g1 in noticias_g1:
            url_g1, noticia = noticia_g1
            nome_arquivo = ''.join(
                url_g1.split('.')[-2].split('/')[-1].replace('-', '_') + '.docx'
            )
            self.__arquivo.nome_arquivo = self.__diretorio + nome_arquivo
            self.__arquivo.noticia = noticia
            self.__arquivo.gerar_documento()
            self.__arquivo()
            self.__api_noticia.salvar_dados(noticia=noticia)

        return True
