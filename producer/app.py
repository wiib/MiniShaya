from flask import Flask, request, jsonify
import pika, json
from datetime import datetime

app = Flask(__name__)

# Conexión a RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.queue_declare(queue="alerts", durable=True)

@app.route("/alert/orange", methods=["POST"])
def orange_alert():
    data = request.json

    message = {
        "type": "alert_orange",
        "sender": data["sender_id"],
        "message": data["message"],
        "timestamp": datetime.utcnow().isoformat()
    }

    channel.basic_publish(
        exchange="",
        routing_key="alerts",
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    return jsonify({"status": "queued"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
