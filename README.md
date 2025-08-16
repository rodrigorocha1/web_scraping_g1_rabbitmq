# Extraindo dados do site do g1 rss e salvando notícias em arquivo docx, usando rabbitmq (Padrão WORK QUEUE)

## 1. Objetivo do projeto

O objetivo deste projeto é demonstrar uma arquitetura distribuída de web scraping para coletar dados de uma URL RSS (ex: [G1 Ribeirão Preto-Franca](https://g1.globo.com/rss/g1/sp/ribeirao-preto-franca/)), obter a notícia do site (ex: [exemplo de notícia](https://g1.globo.com/sp/ribeirao-preto-franca/noticia/2025/08/16/advogado-escapa-ileso-de-ataque-a-tiros-em-ribeirao-preto-video.ghtml)) e salvar o texto em arquivos DOCX.  

O projeto realiza processamento de dados em paralelo e explora os seguintes conceitos e tecnologias:

- Padrão Work Queue com RabbitMQ
- Banco de dados não relacional Redis

---

## 2. Tecnologias utilizadas

- **Python** – Linguagem principal para scraping, processamento e integração.  
- **RabbitMQ** – Sistema de mensageria para coordenar o fluxo de notícias.  
- **Requests + BeautifulSoup** – Para baixar e extrair o conteúdo das matérias.  
- **python-docx** – Para salvar as notícias em arquivos DOCX.  
- **Docker Compose** – Para empacotamento e execução dos serviços.  
- **Redis** – Banco de dados para armazenar URLs de notícias e evitar duplicidade.

---

## 3. Arquitetura da solução

O web scraping distribuído foi dividido em duas funções principais:

1. **Producer**: lê a URL RSS do G1, obtém o link da notícia e envia para a fila do RabbitMQ.  
2. **Consumer (Workers)**: recebem os links da fila, extraem o texto da notícia e salvam em um arquivo DOCX.

---

### 3.1 Requisitos do projeto

#### 3.1.1 Requisitos Funcionais

- **RF1** – Coleta de links de notícias do site do G1 via RSS  
- **RF2** – Publicação dos links na fila, ex: `fila_g1_ribeirao_preto`  
- **RF3** – Consumers recebem os links das notícias  
- **RF4** – Arquivo DOCX gerado com o título da notícia, ex:  Site: **https://g1.globo.com/sp/ribeirao-preto-franca/especial-publicitario/ampere-inteligencia-em-eventos/noticia/2025/08/12/eventos-corporativos-presenciais-sao-estrategicos-para-engajar-clientes-e-equipes.ghtml** Nome do arquivo: **eventos_corporativos_presenciais_sao_estrategicos_para_engajar_clientes_e_equipes.docx**
- **RF5** – Cada notícia fica em uma pasta/diretório de acordo com o nome da fila.

#### 3.1.2 Requisitos Não Funcionais

- **RNF1** – Suportar aumento do número de consumers sem mudanças significativas no código  
- **RNF2** – Processamento de cada notícia em tempo satisfatório: ~3 segundos por worker

---

### 3.2 Diagrama de classes e padrões de projeto usados

[![Diagrama de Classe](https://github.com/rodrigorocha1/web_scraping_g1_rabbitmq/blob/master/diagramas/diagrama_de_classe.jpg?raw=true)](https://github.com/rodrigorocha1/web_scraping_g1_rabbitmq/blob/master/diagramas/diagrama_de_classe.jpg?raw=true)

- **Observer / Work Queue**  
Cada worker processa uma mensagem por vez. Se houver falha na extração ou geração do arquivo, a mensagem vai para a **DLQ (Dead Letter Queue)**.

- **Decorator**  
Na classe `ArquivoDOCX`, antes de salvar, é feita a formatação da notícia: título, subtítulo, autor e texto, aplicando estilos (cores, fontes e alinhamento).

- **Repository**  
A classe `ConexaRedis` abstrai operações de leitura e consulta, isolando a lógica de persistência no Redis.

- **Template Method**  
Presente em `IwebScapingBase` e `WebScrapingBs4Base`. Define o fluxo de web scraping, permitindo que subclasses (`WebScrapingBs4G1Rss`, `WebScrapingG1`) implementem a lógica específica de cada site.

---

### Uso do Redis

- Atua como cache e controle de duplicidade.  
- Estrutura **Set**: coleção ordenada de elementos que garante que cada URL seja armazenada apenas uma vez.

---

## 4. Fluxo resumido

1. Producer consulta o RSS do G1  
2. Links de novas notícias são publicados na fila RabbitMQ  
3. Consumers leem os links da fila  
4. Cada consumer baixa a notícia e extrai título, data e conteúdo  
5. A notícia é armazenada em um arquivo `.docx`, organizada por data  

---

## 5. Benefícios do projeto

- **Escalabilidade** – Possível aumentar o número de consumers para processar mais notícias em paralelo  
- **Desacoplamento** – Producer e consumer não precisam conhecer a lógica entre si  
- **Reuso** – Arquitetura reaproveitável para outros sites e formatos  
- **Portfólio** – Demonstra integração entre scraping, mensageria e geração de documentos

---



## 6. Vídeo com a demonstração do projeto 

[![Assistir ao vídeo de demonstração do projeto](https://img.shields.io/badge/🎬%20Assistir%20ao%20vídeo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/S-rt9kp7MdY)



[Link do reposítório](https://github.com/rodrigorocha1/web_scraping_g1_rabbitmq)