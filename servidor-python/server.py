from flask import Flask, request, jsonify, g
import paho.mqtt.client as mqtt

# Configuración
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# DB mock
CONTACTS_DB = {
    "scaez": ["lquizhpi", "ymacas"],
    "lquizhpi": ["ymacas"],
    "ymacas": ["scaez"]
}

# Inicializar aplicación con Flask
app = Flask(__name__)

def on_connect(client, userdata, flags, rc):
    """Callback cuando el cliente se conecta al broker"""
    if rc == 0:
        print("Conexión establecida con el broker.")
    else:
        print(f"Error al conectar con el broker. {rc=}")

# Cliente MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.on_connect = on_connect

# Conectar al broker
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print("Error al conectar con el broker.")

# === ENDPOINTS ===

@app.route("/alert/orange", methods=["POST"])
def handle_orange_alert():
    """
    Este endpoint recibe una solicitud de alerta naranja de un cliente, y
    publica a los topics MQTT específicos de los contactos del cliente.
    """
    data = request.json
    
    sender_id = data.get("sender_id")
    message = data.get("message")

    if not sender_id or not message:
        return jsonify({ "error": "'sender_id' o 'message' faltantes." }), 400
    
    # Obtener contactos
    contacts = CONTACTS_DB.get(sender_id)

    if not contacts:
        print(f"El usuario {sender_id} no tiene contactos.")
        return jsonify({ "message": "El usuario no tiene contactos." }), 200
    
    # Publicar la alerta en cada topic
    published_to = []
    for contact_id in contacts:
        # app/alert/orange/<receptor>/<emisor>
        topic = f"app/alert/orange/{contact_id}/{sender_id}"

        # Publicar mensaje
        result = mqtt_client.publish(topic, message)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Alerta publicada en {topic}")
            published_to.append(contact_id)
        else:
            print(f"Error al publicar alerta en {topic}")

    return jsonify({
        "message": "Alerta naranja distribuida",
        "sender_id": sender_id,
        "published_to_contacts": published_to
    }), 200

@app.route("/message/orange", methods=["POST"])
def handle_orange_message():
    """
    Este endpoint distribuye mensajes enviados durante una
    alerta naranja.
    """
    data = request.json
    
    sender_id = data.get("sender_id")
    message = data.get("message")

    if not sender_id or not message:
        return jsonify({ "error": "'sender_id' o 'message' faltantes." }), 400
    
    # Obtener contactos
    contacts = CONTACTS_DB.get(sender_id)

    if not contacts:
        print(f"El usuario {sender_id} no tiene contactos.")
        return jsonify({ "message": "El usuario no tiene contactos." }), 200
    
    # Publicar la alerta en cada topic
    published_to = []
    for contact_id in contacts:
        # app/message/orange/<receptor>/<emisor>
        topic = f"app/message/orange/{contact_id}/{sender_id}"

        # Publicar mensaje
        result = mqtt_client.publish(topic, message)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Mensaje publicado en {topic}")
            published_to.append(contact_id)
        else:
            print(f"Error al publicar mensaje en {topic}")

    return jsonify({
        "message": "Mensaje distribuido",
        "sender_id": sender_id,
        "published_to_contacts": published_to
    }), 200

if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("Apagando servidor...")
    finally:
        mqtt_client.loop_stop()
        print("Cliente MQTT desconectado.")
        