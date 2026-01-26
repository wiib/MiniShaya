import pika
import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
import osmnx as ox
from shapely.geometry import Point

RABBIT_HOST = "rabbitmq"
QUEUE_NAME = "alerts"
MQTT_HOST = "mosquitto"

# -------- LOG JSON --------
def log(service, level, event_type, message, extra=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service,
        "level": level,
        "event_type": event_type,
        "message": message
    }
    if extra:
        entry.update(extra)
    print(json.dumps(entry), flush=True)

# -------- GEO --------
class CoordsGenerator:
    def __init__(self):
        log("consumer", "INFO", "GEO_INIT", "Descargando datos geográficos de Cuenca")
        self.gdf = ox.geocode_to_gdf("Cuenca, Azuay, Ecuador")
        self.base_poly = self.gdf.geometry.iloc[0]
        self.min_x, self.min_y, self.max_x, self.max_y = self.base_poly.bounds
        log("consumer", "INFO", "GEO_READY", "Datos geográficos cargados")

    def get_coords(self):
        while True:
            lon = random.uniform(self.min_x, self.max_x)
            lat = random.uniform(self.min_y, self.max_y)
            if self.base_poly.contains(Point(lon, lat)):
                return lat, lon

coords = CoordsGenerator()

# -------- MQTT --------
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_HOST, 1883, 60)
mqtt_client.loop_start()

log("consumer", "INFO", "MQTT_CONNECT", "Conectado a Mosquitto")

# -------- RABBIT --------
def connect_rabbit():
    while True:
        try:
            log("consumer", "INFO", "RABBIT_CONNECT", "Intentando conexión a RabbitMQ")
            conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
            log("consumer", "INFO", "RABBIT_CONNECTED", "Conectado a RabbitMQ")
            return conn
        except pika.exceptions.AMQPConnectionError:
            log("consumer", "ERROR", "RABBIT_RETRY", "RabbitMQ no disponible, reintentando en 5s")
            time.sleep(5)

connection = connect_rabbit()
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

# -------- CALLBACK --------
def callback(ch, method, properties, body):
    event = json.loads(body)

    event["sender"] = event.get("sender", "unknown")
    lat, lon = coords.get_coords()
    event["lat"] = lat
    event["lon"] = lon

    log(
        "consumer", "INFO", "EVENT_RECEIVED",
        "Evento recibido",
        {
            "type": event.get("type"),
            "sender": event.get("sender"),
            "lat": lat,
            "lon": lon
        }
    )

    for topic in event.get("topics", []):
        mqtt_client.publish(topic, json.dumps(event))

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

log("consumer", "INFO", "CONSUMER_READY", "Esperando mensajes")
channel.start_consuming()
