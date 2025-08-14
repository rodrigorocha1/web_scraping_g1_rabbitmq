import time
import random
import pika
import json


RABBITMQ_HOST = 'localhost'
ORDER_QUEUE = 'orders_queue'
EXCHANGE = 'orders_exchange_v2'
DLX_EXCHANGE = 'orders_dead_letter_exchange'

credenciais = pika.PlainCredentials('rodrigo', '123456')
parametros_conexao = pika.ConnectionParameters(
    host='172.30.0.10',
    port=5672,
    virtual_host='/',
    credentials=credenciais
)
conexao = pika.BlockingConnection(parametros_conexao)

canal = conexao.channel()


canal.exchange_declare(exchange=EXCHANGE, exchange_type='direct', durable=True)
canal.exchange_declare(exchange=DLX_EXCHANGE, exchange_type='fanout', durable=True)


canal.queue_declare(queue=ORDER_QUEUE, durable=True, arguments={
    'x-dead-letter-exchange': DLX_EXCHANGE
})
canal.queue_bind(exchange=EXCHANGE, queue=ORDER_QUEUE, routing_key='orders')

canal.queue_declare(queue='orders_dlq', durable=True)
canal.queue_bind(exchange=DLX_EXCHANGE, queue='orders_dlq')

# Função para processar pedidos
def process_order(ch, method, properties, body):
    order = json.loads(body)
    print(f"[>] Processando pedido: {order}")

    # Simula falha aleatória
    if random.choice([True, False]):
        print(f"[!] Falha no pedido {order['order_id']}, enviando para DLX.")
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print(f"[v] Pedido {order['order_id']} processado com sucesso!")
        ch.basic_ack(delivery_tag=method.delivery_tag)

canal.basic_qos(prefetch_count=1)
canal.basic_consume(queue=ORDER_QUEUE, on_message_callback=process_order)

if __name__ == "__main__":
    print("[*] Aguardando pedidos...")
    canal.start_consuming()