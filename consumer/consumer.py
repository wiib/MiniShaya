import pika
import json
import time
import random
import os
import paho.mqtt.client as mqtt

# --- Config ---
RABBIT_HOST = "localhost"
QUEUE_NAME = "alerts"

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

CONSUMER_ID = os.getenv("HOSTNAME", f"consumer-{random.randint(1000,9999)}")

# --- MQTT ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# --- RabbitMQ ---
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBIT_HOST)
)
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

print(f"[{CONSUMER_ID}] Esperando mensajes...")

def heavy_computation():
    """Simula carga para HPA"""
    total = 0
    for _ in range(10_000_000):
        total += random.randint(1, 10)
    return total

def callback(ch, method, properties, body):
    data = json.loads(body)

    print(f"[{CONSUMER_ID}] Mensaje recibido: {data}")

    # 🔥 carga artificial
    heavy_computation()

    # Publicar en MQTT
    topic = "app/alert/orange/" + data["sender"]
    mqtt_client.publish(topic, data["message"])

    print(f"[{CONSUMER_ID}] Publicado en MQTT")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

channel.start_consuming()
