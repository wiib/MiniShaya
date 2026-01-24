import pika
import json
import time
import paho.mqtt.client as mqtt

RABBIT_HOST = "rabbitmq"
QUEUE_NAME = "alerts"
MQTT_HOST = "mosquitto"

# ---------- MQTT ----------
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_HOST, 1883, 60)
mqtt_client.loop_start()

print("[CONSUMER] Conectado a Mosquitto")

# ---------- RABBITMQ (REINTENTO REAL) ----------
def connect_rabbit():
    while True:
        try:
            print("[CONSUMER] Conectando a RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST)
            )
            print("[CONSUMER] Conectado a RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("[CONSUMER] RabbitMQ no disponible, reintentando...")
            time.sleep(5)

connection = connect_rabbit()
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

# ---------- CALLBACK ----------
def callback(ch, method, properties, body):
    event = json.loads(body)

    for topic in event["topics"]:
        mqtt_client.publish(topic, json.dumps(event))
        print(f"[CONSUMER] MQTT → {topic}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

# ---------- CONSUMO ----------
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

print("[CONSUMER] Esperando mensajes...")
channel.start_consuming()
