from flask import Flask, request, jsonify
import pika
import json
import time
from datetime import datetime, timezone

RABBIT_HOST = "rabbitmq"
QUEUE_NAME = "alerts"

CONTACTOS = {
    "Luis": ["app/alert/orange/Yuzabeth", "app/alert/orange/Sebastian"],
    "Yuzabeth": ["app/alert/orange/Luis"],
    "Sebastian": ["app/alert/orange/Luis"],
}

def get_channel():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            print("[PRODUCER] Conectado a RabbitMQ")
            return channel
        except pika.exceptions.AMQPConnectionError:
            print("[PRODUCER] RabbitMQ no disponible, reintentando...")
            time.sleep(5)

app = Flask(__name__)

@app.route("/alert/orange", methods=["POST"])
def orange_alert():
    data = request.json
    sender = data["sender_id"]
    message = data["message"]

    event = {
        "type": "orange",
        "message": message,
        "topics": CONTACTOS.get(sender, []),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    channel = get_channel()
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    return jsonify({"status": "queued", "targets": event["topics"]}), 200


@app.route("/alert/red", methods=["POST"])
def red_alert():
    data = request.json

    event = {
        "type": "red",
        "message": data["message"],
        "topics": ["app/alert/red/global"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sender": data["sender_id"]
    }

    channel = get_channel()
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    return jsonify({"status": "queued"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
