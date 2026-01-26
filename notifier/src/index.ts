import express from "express";
import { createServer } from "http";
import mqtt from "mqtt";
import { Server } from "socket.io";

const MQTT_BROKER = "mqtt://mosquitto:1883";
const MQTT_ORANGE_TOPIC = "app/alert/orange/#";
const MQTT_RED_TOPIC = "app/alert/red/#";
const PORT = 3001;

interface OrangeAlertData {
  type: string;
  sender: string;
  message: string;
  timestamp: string;
  lat: number;
  lon: number;
}

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
  },
});

const mqttClient = mqtt.connect(MQTT_BROKER);

mqttClient.on("connect", () => {
  console.log(`Conectado al broker MQTT: ${MQTT_BROKER}`);

  const topics = [MQTT_ORANGE_TOPIC, MQTT_RED_TOPIC];

  mqttClient.subscribe(topics, (err) => {
    if (err instanceof Error) {
      console.error("Error de suscripción (alertas naranjas): ", err);
    } else {
      console.log(`Suscrito a los topics: ${topics}`);
    }
  });
});

mqttClient.on("message", (topic, buffer) => {
  const payloadJson = JSON.parse(buffer.toString());
  const alertType = payloadJson.type;

  const data: OrangeAlertData = {
    message: payloadJson.message,
    sender: payloadJson.sender,
    timestamp: payloadJson.timestamp,
    type: payloadJson.type,
    lat: payloadJson.lat,
    lon: payloadJson.lon,
  };

  console.log(`Notificando: [${topic}]`, data);

  if (alertType === "red") {
    io.emit("red-alert", data);
  } else if (alertType === "orange") {
    io.emit("orange-alert", data);
  }
});

httpServer.listen(PORT, () => {
  console.log(`Notificador ejecutándose en http://localhost:${PORT}`);
});
