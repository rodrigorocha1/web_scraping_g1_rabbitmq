import pika
import json
import time

ORDER_QUEUE = 'orders_queue'
EXCHANGE = 'orders_exchange_v2'



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
canal.queue_declare(queue=ORDER_QUEUE, durable=True, arguments={
    'x-dead-letter-exchange': 'orders_dead_letter_exchange'
})
canal.queue_bind(exchange=EXCHANGE, queue=ORDER_QUEUE, routing_key='orders')  # roteamento consistente

def send_order(order_id):
    message = {"order_id": order_id, "item": "Produto X"}
    canal.basic_publish(
        exchange=EXCHANGE,
        routing_key='orders',
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"[x] Pedido enviado: {message}")

if __name__ == "__main__":
    order_id = 1
    print("[*] Enviando pedidos continuamente...")
    while True:
        send_order(order_id)
        order_id += 1
        time.sleep(0.5)