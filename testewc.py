import requests
import json

url = "http://127.0.0.1:8000/login"

payload = {
    "username": "rodrigo",
    "senha": "12346"
}
headers = {
    'Content-Type': 'application/json'
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=5)

    # Levanta exceção para status codes 4xx/5xx
    response.raise_for_status()

    try:
        data = response.json()
        print("Resposta JSON:", data)
    except ValueError:
        print("A resposta não está em formato JSON.")
        print("Resposta bruta:", response.text)

except requests.exceptions.ConnectionError as e:

    print(f"Erro: Não foi possível conectar ao servidor.{e}")
    print(f'{response.content}')
except requests.exceptions.Timeout:
    print("Erro: Tempo limite da requisição excedido.")
except requests.exceptions.HTTPError as http_err:
    print(f"Erro HTTP: {http_err} - Status Code: {response.status_code}")
    print("Resposta do servidor:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Ocorreu um erro inesperado: {e}")

