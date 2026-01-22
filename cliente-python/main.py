import customtkinter as ctk
import paho.mqtt.client as mqtt
import requests
import threading
import time
from datetime import datetime
import Pyro5.api

# --- Configuración ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_BASE = "app"

# --- Colores ---
RED_BG = "#631c1c"
ORANGE_BG = "#883a1b"
DEFAULT_BG = "#242424"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

ns = Pyro5.api.locate_ns()
uri = ns.lookup("my.mqtt.publisher")

mqtt_publisher = Pyro5.api.Proxy(uri)


class AlertClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cliente SHAYA")
        self.geometry("900x700")

        self.minsize(900, 700)
        self.maxsize(900, 700)

        # Estado
        self.user_id = None
        self.mqtt_client = None
        self.is_connected = False

        self.red_active = None
        self.orange_active = None

        self._init_ui()

    def _init_ui(self):
        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Barra lateral
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Sistema de Alertas",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.user_id_entry = ctk.CTkEntry(self.sidebar, placeholder_text="ID Usuario")
        self.user_id_entry.grid(row=1, column=0, padx=20, pady=10)

        self.connect_btn = ctk.CTkButton(
            self.sidebar, text="Conectar", command=self.start_connection
        )
        self.connect_btn.grid(row=2, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(
            self.sidebar, text="Estado: Desconectado", text_color="gray"
        )
        self.status_label.grid(row=3, column=0, padx=20, pady=10)

        # Contenido principal
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_rowconfigure(3, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(1, weight=1)

        # Botones
        self.red_btn = ctk.CTkButton(
            self.main_area,
            text="🚨 ENVIAR ALERTA ROJA",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            height=80,
            font=ctk.CTkFont(size=20, weight="bold"),
            state="disabled",
            command=self.send_red_alert,
        )
        self.red_btn.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10)
        )

        self.orange_btn = ctk.CTkButton(
            self.main_area,
            text="⚠️ ENVIAR ALERTA NARANJA",
            fg_color="#ea580c",
            hover_color="#c2410c",
            height=60,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled",
            command=self.send_orange_alert,
        )
        self.orange_btn.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 20)
        )

        self.cancel_btn = ctk.CTkButton(
            self.main_area,
            text="🚫 CANCELAR ALERTA",
            fg_color="#323232",
            hover_color="#424242",
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled",
            command=self.cancel_alerts,
        )
        self.cancel_btn.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 20)
        )

        # Área de mensajes
        self.msg_frame = ctk.CTkFrame(self.main_area)
        self.msg_frame.grid(
            row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10)
        )
        self.msg_frame.grid_columnconfigure(0, weight=1)

        self.msg_label = ctk.CTkLabel(
            self.msg_frame, text="Alerta Naranja — Mensajes", anchor="w"
        )
        self.msg_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.msg_entry = ctk.CTkEntry(
            self.msg_frame, placeholder_text="Envía mensajes a tus contactos..."
        )
        self.msg_entry.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=10)

        # Enviar con Enter
        self.msg_entry.bind("<Return>", lambda event: self.send_orange_message())

        self.send_msg_btn = ctk.CTkButton(
            self.msg_frame,
            text="Enviar",
            width=80,
            state="disabled",
            command=self.send_orange_message,
        )
        self.send_msg_btn.grid(row=1, column=1, sticky="e", padx=(5, 10), pady=10)

        # Área de log
        self.log_label = ctk.CTkLabel(self.main_area, text="Log de alertas", anchor="w")
        self.log_label.grid(row=4, column=0, sticky="w", padx=10)

        self.log_box = ctk.CTkTextbox(self.main_area, state="disabled")
        self.log_box.grid(
            row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 0)
        )

    # --- Configuración de MQTT ---

    def start_connection(self):
        user_id_input = self.user_id_entry.get().strip()
        if not user_id_input:
            self.log_message("SISTEMA", "Ingresa un ID de usuario")
            return

        if self.is_connected:
            self.disconnect()
        else:
            self.user_id = user_id_input
            self.connect_mqtt()

    def connect_mqtt(self):
        self.connect_btn.configure(state="disabled", text="Conectando...")
        self.status_label.configure(text="Estado: Conectando...", text_color="yellow")

        # Asignar un ID único al cliente
        client_id = f"{self.user_id}_{int(time.time())}"
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect

        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()  # HILO PARA MQTT
        except Exception as e:
            self.log_message("ERROR", f"No se pudo conectar con el broker: {e}")
            self.disconnect()

    def disconnect(self):
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        self.is_connected = False
        self.update_ui_connect(connected=False)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True

            # AGENDAR ACTUALIZACIONES DE UI EN EL HILO PRINCIPAL
            self.after(0, lambda: self.update_ui_connect(connected=True))
            self.after(
                0, lambda: self.log_message("SISTEMA", f"Conectado como {self.user_id}")
            )

            # --- Suscripciones ---
            # app/alert/red/+ -- Recibo todas las alertas rojas
            client.subscribe(f"{TOPIC_BASE}/alert/red/+")

            # app/alert/orange/<receptor>/+ -- Recibo alertas naranja dirigidas hacia mi
            client.subscribe(f"{TOPIC_BASE}/alert/orange/{self.user_id}/+")

            # app/alert/cancel/+ -- Recibo cancelaciones de alertas
            client.subscribe(f"{TOPIC_BASE}/cancel/red/+")
            client.subscribe(f"{TOPIC_BASE}/cancel/orange/+")

            # app/message/orange/<receptor>/+ -- Recibo mensajes naranja dirigidos hacia mi
            client.subscribe(f"{TOPIC_BASE}/message/orange/{self.user_id}/+")

        else:
            self.after(
                0, lambda: self.log_message("ERROR", f"Conexión fallida con {rc=}")
            )
            self.disconnect()

    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        self.after(0, lambda: self.update_ui_connect(connected=False))
        if rc != 0:
            self.after(
                0, lambda: self.log_message("SISTEMA", "Desconexión inesperada!")
            )

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        # Dividir topic en partes
        parts = topic.split("/")

        msg_type = parts[1]  # 'alert', 'message', 'cancel'
        severity = parts[2]  # 'red' u 'orange'

        sender = "Desconocido"
        if severity == "red":
            # app/alert/red/<emisor>
            sender = parts[3]
            self.red_active = sender

        elif severity == "orange":

            if msg_type != "cancel":
                # app/alert/orange/<receptor>/<emisor>
                sender = parts[4]
            else:
                # app/cancel/orange/<emisor>
                sender = parts[3]
            self.orange_active = sender

        if msg_type == "cancel":
            self.red_active = None
            self.orange_active = None

        # Formato de log
        display_type = f"[{severity.upper()} {msg_type.upper()}]"
        self.after(0, lambda: self.log_message(sender, payload, prefix=display_type))
        self.after(0, lambda: self.update_ui_bg())
        self.after(0, lambda: self.update_ui_buttons())
        self.after(0, lambda: self.update_ui_msg_entry())

    # --- Métodos para UI ---

    def update_ui_connect(self, connected):
        state = "normal" if connected else "disabled"
        btn_text = "Desconectar" if connected else "Conectar"
        status_txt = "Estado: Conectado" if connected else "Estado: Desconectado"
        status_col = "#22c55e" if connected else "gray"  # Green if connected

        self.connect_btn.configure(text=btn_text, state="normal")
        self.status_label.configure(text=status_txt, text_color=status_col)
        self.user_id_entry.configure(state="disabled" if connected else "normal")

        self.red_btn.configure(state=state)
        self.orange_btn.configure(state=state)
        self.send_msg_btn.configure(state=state)

    def update_ui_bg(self):
        color = DEFAULT_BG

        if self.red_active and self.red_active != self.user_id:
            color = RED_BG
        elif self.orange_active and self.orange_active != self.user_id:
            color = ORANGE_BG

        self.main_area.configure(bg_color=color)

    def update_ui_buttons(self):
        if self.orange_active == self.user_id or self.red_active == self.user_id:
            self.red_btn.configure(state="disabled")
            self.orange_btn.configure(state="disabled")
            self.cancel_btn.configure(state="enabled")
        else:
            self.red_btn.configure(state="enabled")
            self.orange_btn.configure(state="enabled")
            self.cancel_btn.configure(state="disabled")

    def update_ui_msg_entry(self):
        if self.orange_active == self.user_id:
            self.msg_entry.configure(state="normal")
            self.send_msg_btn.configure(state="normal")
        else:
            self.msg_entry.configure(state="disabled")
            self.send_msg_btn.configure(state="disabled")

    def log_message(self, sender, message, prefix="[INFO]"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_text = f"{timestamp} {prefix} {sender}: {message}\n"

        self.log_box.configure(state="normal")
        self.log_box.insert("end", full_text)
        self.log_box.see("end")  # Auto-scroll to bottom
        self.log_box.configure(state="disabled")

    # --- Handlers ---

    def send_red_alert(self):
        self.red_active = self.user_id

        # Se envía directo al broker
        topic = f"{TOPIC_BASE}/alert/red/{self.user_id}"
        payload = "NECESITO AYUDA URGENTE! Alerta roja iniciada."
        self.mqtt_client.publish(topic, payload, retain=False)

        self.after(0, lambda: self.update_ui_msg_entry())

        self.log_message("Yo", payload, prefix="[ENVIO ROJA]")

    def send_orange_alert(self):
        self.orange_active = self.user_id

        # Se envía al back para distribuir a contactos
        payload = {
            "sender_id": self.user_id,
            "message": "AUXILIO! Alerta naranja iniciada.",
        }

        self.after(0, lambda: self.update_ui_buttons())
        self.after(0, lambda: self.update_ui_msg_entry())

        mqtt_publisher.send_orange_alert(payload["sender_id"], payload["message"])

    def cancel_alerts(self):
        alert = "orange" if self.orange_active == self.user_id else "red"
        payload = "He cancelado la alerta."

        topic = f"{TOPIC_BASE}/cancel/{alert}/{self.user_id}"
        self.mqtt_client.publish(topic, payload, retain=False)

        self.after(0, lambda: self.update_ui_msg_entry())

        self.log_message("Yo", payload, prefix="[CANCELA ALERTA]")

    def send_orange_message(self):
        msg = self.msg_entry.get()
        if not msg:
            return

        payload = {"sender_id": self.user_id, "message": msg}

        self.msg_entry.delete(0, "end")

        mqtt_publisher.send_orange_message(payload["sender_id"], payload["message"])


app = AlertClientApp()
app.mainloop()
