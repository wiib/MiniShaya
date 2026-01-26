from flask import Flask, request, jsonify
from flask_cors import CORS
import pika
import json
import time
from datetime import datetime, timezone

# ---------------- CONFIG ----------------
RABBIT_HOST = "rabbitmq"
QUEUE_NAME = "alerts"

# ---------------- CONTACTOS ----------------
CONTACTOS = {
    "Luis": ["app/alert/orange/Yuzabeth", "app/alert/orange/Sebastian"],
    "Yuzabeth": ["app/alert/orange/Luis"],
    "Sebastian": ["app/alert/orange/Luis"],
}

# ---------------- LOG HELPER (JSON) ----------------
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

# ---------------- RABBITMQ ----------------
def get_channel():
    while True:
        try:
            log(
                service="producer",
                level="INFO",
                event_type="RABBIT_CONNECT",
                message="Intentando conexión a RabbitMQ"
            )

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            log(
                service="producer",
                level="INFO",
                event_type="RABBIT_CONNECTED",
                message="Conectado a RabbitMQ"
            )

            return channel

        except pika.exceptions.AMQPConnectionError:
            log(
                service="producer",
                level="ERROR",
                event_type="RABBIT_RETRY",
                message="RabbitMQ no disponible, reintentando en 5s"
            )
            time.sleep(5)

# ---------------- FLASK ----------------
app = Flask(__name__)
CORS(app, origins="*")

# ---------- ALERTA NARANJA ----------
@app.route("/alert/orange", methods=["POST"])
def orange_alert():
    data = request.json

    sender = data["sender_id"]
    message = data["message"]
    targets = CONTACTOS.get(sender, [])

    event = {
        "type": "orange",
        "sender": sender,
        "message": message,
        "topics": targets,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    channel = get_channel()
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    log(
        service="producer",
        level="INFO",
        event_type="ALERT_ORANGE",
        message="Alerta naranja enviada",
        extra={
            "sender": sender,
            "targets": targets
        }
    )

    return jsonify({"status": "queued", "targets": targets}), 200


# ---------- ALERTA ROJA ----------
@app.route("/alert/red", methods=["POST"])
def red_alert():
    data = request.json

    message = data.get("message", "")

    event = {
        "type": "red",
        "message": message,
        "topics": ["app/alert/red/global"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    channel = get_channel()
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    log(
        service="producer",
        level="INFO",
        event_type="ALERT_RED",
        message="Alerta roja enviada (broadcast)"
    )

    return jsonify({"status": "queued"}), 200


# ---------------- MAIN ----------------
if __name__ == "__main__":
    log(
        service="producer",
        level="INFO",
        event_type="SERVICE_START",
        message="Producer iniciado en puerto 5000"
    )
    app.run(host="0.0.0.0", port=5000)
