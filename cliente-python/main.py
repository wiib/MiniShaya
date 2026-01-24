import requests
import json
import paho.mqtt.client as mqtt
import tkinter as tk
from datetime import datetime

API_URL = "http://localhost:5000"

def log(msg):
    output.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} {msg}\n")
    output.see(tk.END)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    log(f"[MQTT] {data['type'].upper()} → {data['message']}")

def connect_mqtt():
    user = username.get()
    client = mqtt.Client()
    client.on_message = on_message

    client.connect("localhost", 1883, 60)

    client.subscribe("app/alert/red/global")
    client.subscribe(f"app/alert/orange/{user}")

    client.loop_start()
    log("[SISTEMA] Conectado a Mosquitto")

def send_red():
    requests.post(f"{API_URL}/alert/red", json={"message": "ALERTA ROJA"})
    log("[HTTP] Alerta roja enviada (GLOBAL)")

def send_orange():
    requests.post(
        f"{API_URL}/alert/orange",
        json={"sender_id": username.get(), "message": "Alerta naranja"}
    )
    log("[HTTP] Alerta naranja enviada (CONTACTOS)")

root = tk.Tk()
root.title("Cliente SHAYA")

username = tk.Entry(root)
username.pack()

tk.Button(root, text="Conectar MQTT", command=connect_mqtt).pack()
tk.Button(root, text="Enviar Alerta Roja", command=send_red).pack()
tk.Button(root, text="Enviar Alerta Naranja", command=send_orange).pack()

output = tk.Text(root, height=10)
output.pack()

root.mainloop()
