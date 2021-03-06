import pika
from pika.exchange_type import ExchangeType
from pika.delivery_mode import DeliveryMode


auth = pika.PlainCredentials("guest", "guest")
conn = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="shostakovich", port=5672, virtual_host="/", credentials=auth
    )
)
channel = conn.channel()
channel.confirm_delivery()
channel.exchange_declare(
    exchange="backup_exchange",
    exchange_type=ExchangeType.fanout,
    durable=True,
)
channel.queue_declare(
    queue="backup_queue",
    durable=True,
)
channel.queue_bind(
    queue="backup_queue", exchange="backup_exchange", routing_key="ignored-by-fanout"
)
channel.exchange_declare(
    exchange="master_exchange",
    exchange_type=ExchangeType.direct,
    durable=True,
    arguments={"alternate-exchange": "backup_exchange"},
)
channel.queue_declare(
    queue="master_queue",
    durable=True,
)
channel.queue_bind(
    queue="master_queue", exchange="master_exchange", routing_key="master_queue"
)
message = "hello world"
channel.basic_publish(
    exchange="master_exchange",
    # unreachable route
    routing_key="backup_queue",
    body=message.encode(),
    properties=pika.BasicProperties(
        delivery_mode=DeliveryMode.Persistent,
    ),
)
conn.close()
