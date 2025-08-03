# Proposta de Arquitetura para Web Scraping do G1 com Padrão Chain of Responsibility (Cadeia de reponsabilidade)


## 1. Objetivo do Projeto

- Criar um pipeline de dados fácil de realizar manutenção, ou seja, estruturado, modular e escalável.  
- Discutir o padrão de projeto **Cadeia de Responsabilidade (Chain of Responsibility)**.  
- Gerar um arquivo `.docx` para cada notícia do G1.  
- Rastrear eventos de log em um banco de dados:  
  - Ex: **Sucesso de conexão da API**, **erro de conexão da API**, **consultar a notícia na API**, **salvar a notícia na API**.  
- Gravar a notícia em uma **API Simulada**.  

---

## 2. Arquitetura / Estrutura Técnica

### 2.1 Tecnologias Usadas
- **Linguagem:** Python  
- **Extração:** BeautifulSoup  
- **Banco de dados:** SQLite para registro do log  
- **API Simulada:** para inserir as notícias  

---

## 3. Arquitetura do Pipeline

### 3.1 Diagrama de Classe
[![Diagrama de Classe](https://github.com/rodrigorocha1/web_scraping_g1/blob/master/diagramas/diagrama_de_classe.jpg?raw=true)](https://github.com/rodrigorocha1/web_scraping_g1/blob/master/diagramas/diagrama_de_classe.jpg?raw=true)

---

O padrão **Cadeia de Responsabilidade (Chain of Responsibility)** permite criar um fluxo composto por múltiplos manipuladores, onde cada manipulador é uma etapa de processamento de web scraping.  

As etapas listadas são:
- **Checagem de conexão da API**  
- **Obter XML do site RSS do G1**  
- **Extrair link do conteúdo da notícia**  
- **Verificar se a notícia já existe**  
- **Salvar a notícia (API simulada e gerar .docx)**  

**Benefícios:**
- Alta coesão e baixo acoplamento  
- Extensibilidade: fácil adicionar novas etapas sem alterar a lógica principal  
- Reuso: fluxo reaproveitável para outros sites de notícias  

---

### 3.2 Diagrama de Atividade
[![Diagrama de Classe](https://github.com/rodrigorocha1/web_scraping_g1/blob/master/diagramas/diagrama_de_atividade.jpg?raw=true)](https://github.com/rodrigorocha1/web_scraping_g1/blob/master/diagramas/diagrama_de_atividade.jpg?raw=true)

O diagrama mostra como será o processo do web scraping:  
1. Conexão do site RSS: caso a conexão seja feita com sucesso, continua o web scraping; caso contrário, encerra o processo.  
2. Conexão do RSS + Parseamento (converter para formato legível).  
3. Conexão da URL do G1 presente no feed RSS.  
4. Verificação se a notícia está cadastrada:  
   - **Se existe:** não salva na API e encerra.  
   - **Se não existe:** cadastra uma nova notícia e encerra o fluxo.  

---

## 4. Principais Funcionalidades

### Requisitos Funcionais
- Implementar busca pela URL.  
- Verificar se a notícia está cadastrada; caso contrário, cadastrar.  
- Validar texto da notícia.  
- Salvar a notícia com os campos:  
  - **id_noticia**, **título**, **subtítulo**, **texto**, **autor**, **data_hora**.  
- Implementar tratamento de erros em todas as etapas.  

---

## 5. Requisitos Não Funcionais
- O código deve seguir os princípios **SOLID**.  
- Utilizar o padrão **Cadeia de Responsabilidade**.  
- Código com tipagem estática e documentação.  
- O ETL não deve precisar de refatoração extensa caso novos sites RSS sejam adicionados.  
- Suporte extensível a outros sites RSS para extração.  
- Todas as credenciais de acesso devem ser protegidas.  

---

## 6. Exemplo Simplificado do Código

```python

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

```




## 7. Vídeo com a demonstração do projeto 
 [![Assistir ao vídeo de demonstração do projeto](https://img.shields.io/badge/🎬%20Assistir%20ao%20vídeo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/S-rt9kp7MdY)

<div style="text-align:center;"> 



[Link do reposítório](https://github.com/rodrigorocha1/web_scraping_g1)
