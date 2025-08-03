from bs4 import BeautifulSoup
from bs4.element import ResultSet
import requests
import re

url = 'https://g1.globo.com/sp/ribeirao-preto-franca/noticia/2025/07/20/tarifaco-de-trump-suspende-exportacoes-de-pescados-em-rifaina-sp-empresa-preve-prejuizos-na-regiao-balde-de-agua-fria.ghtml'

response = requests.get(url=url)
conteudo_response = response.content
soup = BeautifulSoup(conteudo_response, 'html.parser')

texto_noticia = soup.select('p.content-text__container')
print(type(texto_noticia))
lista_texto = []
for texto in texto_noticia:
    if not texto.find('ul') and not texto.find('div.content-intertitle') and "LEIA TAMBÉM:" not in texto.text:
        lista_texto.append(texto.text.strip())

padroes_a_remover = [
    r'✅\s*Clique aqui para seguir o canal do g1 Ribeirão e Franca no WhatsApp',
    r'Veja mais notícias da região no g1 Ribeirão Preto e Franca',
    r'VÍDEOS: Tudo sobre Ribeirão Preto, Franca e região'
]

texto_completo = '\n'.join(lista_texto) # Use a different variable name to avoid confusion

# Remove as frases indesejadas
texto_limpo = texto_completo # Initialize texto_limpo with the full text before cleaning
for padrao in padroes_a_remover:
    texto_limpo = re.sub(padrao, '', texto_limpo, flags=re.IGNORECASE)

print(texto_limpo)