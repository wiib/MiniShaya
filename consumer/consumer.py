import pika
import json
import time
import paho.mqtt.client as mqtt

import random
import osmnx as ox
from shapely.geometry import Point

class CoordsGenerator:
    def __init__(self):
        print("Descargando datos geográficos")

        self.gdf = ox.geocode_to_gdf("Cuenca, Azuay, Ecuador")
        self.base_poly = self.gdf.geometry.iloc[0]

        self.min_x, self.min_y, self.max_x, self.max_y = self.base_poly.bounds
        print("Datos geográficos cargados")

    def get_coords(self):
        while True:
            lon = random.uniform(self.min_x, self.max_x)
            lat = random.uniform(self.min_y, self.max_y)

            pt = Point(lon, lat)

            if self.base_poly.contains(pt):
                return lat, lon

RABBIT_HOST = "rabbitmq"
QUEUE_NAME = "alerts"
MQTT_HOST = "mosquitto"

coords_generator = CoordsGenerator()

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

    lat, lon = coords_generator.get_coords()
    event["lat"] = lat
    event["lon"] = lon

    for topic in event["topics"]:
        mqtt_client.publish(topic, json.dumps(event))
        print(f"[CONSUMER] MQTT → {topic}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

# ---------- CONSUMO ----------
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

print("[CONSUMER] Esperando mensajes...")
channel.start_consuming()
