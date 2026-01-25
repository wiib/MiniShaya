package org.shaya;

import org.eclipse.paho.client.mqttv3.*;

import java.util.*;

public class ShayaMqttClient {

    private MqttClient client;
    private String userId;

    // Handlers que el controller implementa con lambdas
    private final AlertHandler alertHandler;
    private final MessageHandler messageHandler;
    private final CancelHandler cancelHandler;

    // Interfaces funcionales
    public interface AlertHandler { void handle(String sender, String type); }
    public interface MessageHandler { void handle(String sender, String message); }
    public interface CancelHandler { void handle(); }

    // Replica de CONTACTS_DB de Python
    private static final Map<String, List<String>> CONTACTS_DB = new HashMap<>();
    static {
        CONTACTS_DB.put("scaez", Arrays.asList("lquizhpi", "ymacas"));
        CONTACTS_DB.put("lquizhpi", Collections.singletonList("ymacas"));
        CONTACTS_DB.put("ymacas", Collections.singletonList("scaez"));
    }

    public ShayaMqttClient(AlertHandler a, MessageHandler m, CancelHandler c) {
        this.alertHandler = a;
        this.messageHandler = m;
        this.cancelHandler = c;
    }

    // -------------------------------------------------
    // CONEXIÓN
    // -------------------------------------------------
    public void connect(String userId) {
        try {
            this.userId = userId;

            client = new MqttClient("tcp://localhost:1883", userId);

            MqttConnectOptions opts = new MqttConnectOptions();
            opts.setAutomaticReconnect(true);
            opts.setCleanSession(true);

            client.setCallback(new MqttCallback() {
                @Override
                public void connectionLost(Throwable cause) {
                    System.out.println("[JAVA] Conexión MQTT perdida: " + cause);
                }

                @Override
                public void messageArrived(String topic, MqttMessage message) {
                    String payload = new String(message.getPayload());
                    System.out.println("[JAVA] Mensaje recibido en " + topic + " => " + payload);

                    String[] parts = topic.split("/"); // app / alert | message | cancel / ...

                    if (parts.length < 3) {
                        return;
                    }

                    String main = parts[1];  // alert / message / cancel
                    String type = parts[2];  // red / orange / ...

                    // ---------------- ALERTAS ----------------
                    if (main.equals("alert")) {
                        if ("red".equals(type)) {
                            // app/alert/red/<emisor>
                            if (parts.length >= 4) {
                                String sender = parts[3];
                                alertHandler.handle(sender, "ROJA");
                            }
                            return;
                        }

                        if ("orange".equals(type)) {
                            // app/alert/orange/<receptor>/<emisor>
                            if (parts.length >= 5) {
                                String receptor = parts[3];
                                String sender = parts[4];

                                // Solo me interesa si soy el receptor
                                if (receptor.equals(userId)) {
                                    alertHandler.handle(sender, "NARANJA");
                                }
                            }
                            return;
                        }
                    }

                    // ---------------- CANCELACIONES ----------------
                    if (main.equals("cancel")) {
                        // app/cancel/red/<emisor> o app/cancel/orange/<emisor>
                        cancelHandler.handle();
                        return;
                    }

                    // ---------------- MENSAJES NARANJA ----------------
                    if (main.equals("message") && "orange".equals(type)) {
                        // app/message/orange/<receptor>/<emisor>
                        if (parts.length >= 5) {
                            String receptor = parts[3];
                            String sender = parts[4];

                            if (receptor.equals(userId)) {
                                messageHandler.handle(sender, payload);
                            }
                        }
                    }
                }

                @Override
                public void deliveryComplete(IMqttDeliveryToken token) { }
            });

            client.connect(opts);

            // SUSCRIPCIONES IGUALES QUE EL CLIENTE PYTHON
            client.subscribe("app/alert/red/+");
            client.subscribe("app/alert/orange/" + userId + "/+");
            client.subscribe("app/cancel/red/+");
            client.subscribe("app/cancel/orange/+");
            client.subscribe("app/message/orange/" + userId + "/+");

            System.out.println("[JAVA] Suscrito para usuario: " + userId);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void disconnect() {
        try {
            if (client != null && client.isConnected()) {
                client.disconnect();
            }
        } catch (Exception ignored) { }
    }

    private List<String> getContactsFor(String senderId) {
        return CONTACTS_DB.getOrDefault(senderId, Collections.emptyList());
    }

    // -------------------------------------------------
    // ENVÍO DE ALERTAS
    // -------------------------------------------------

    // Alerta roja: mismo patrón que Python: app/alert/red/<emisor>
    public void sendRedAlert(String senderId) {
        String topic = "app/alert/red/" + senderId;
        String msg = "NECESITO AYUDA URGENTE! Alerta roja iniciada.";
        publish(topic, msg);
    }

    // Alerta naranja: se envía a cada contacto: app/alert/orange/<receptor>/<emisor>
    public void sendOrangeAlert(String senderId) {
        List<String> contacts = getContactsFor(senderId);

        if (contacts.isEmpty()) {
            System.out.println("[JAVA] Usuario " + senderId + " no tiene contactos configurados.");
            return;
        }

        String msg = "AUXILIO! Alerta naranja iniciada.";

        for (String contact : contacts) {
            String topic = "app/alert/orange/" + contact + "/" + senderId;
            publish(topic, msg);
        }
    }

    // Cancelar alerta: app/cancel/{alert}/<emisor>
    public void sendCancelAlert(String senderId, boolean isOrange) {
        String alertType = isOrange ? "orange" : "red";
        String topic = "app/cancel/" + alertType + "/" + senderId;
        String msg = "He cancelado la alerta.";
        publish(topic, msg);
    }

    // -------------------------------------------------
    // ENVÍO DE MENSAJES NARANJA
    // -------------------------------------------------

    // Igual que tu servidor Python: app/message/orange/<receptor>/<emisor>
    public void sendOrangeMessage(String senderId, String message) {
        List<String> contacts = getContactsFor(senderId);

        if (contacts.isEmpty()) {
            System.out.println("[JAVA] Usuario " + senderId + " no tiene contactos para mensajes.");
            return;
        }

        for (String contact : contacts) {
            String topic = "app/message/orange/" + contact + "/" + senderId;
            publish(topic, message);
        }
    }

    // -------------------------------------------------
    // AUXILIAR
    // -------------------------------------------------
    private void publish(String topic, String msg) {
        try {
            if (client != null && client.isConnected()) {
                System.out.println("[JAVA] Publicando en " + topic + " => " + msg);
                client.publish(topic, msg.getBytes(), 1, false);
            } else {
                System.out.println("[JAVA] Cliente MQTT no conectado, no se puede publicar.");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
