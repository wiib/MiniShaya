package org.shaya;

import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.layout.AnchorPane;

public class ShayaController {

    @FXML private TextField userIdField;
    @FXML private Button connectButton;

    @FXML private Button redButton;
    @FXML private Button orangeButton;
    @FXML private Button cancelButton;

    @FXML private TextField messageField;
    @FXML private Button sendMessageButton;

    @FXML private TextArea logArea;
    @FXML private AnchorPane bgPane;

    private ShayaMqttClient mqttClient;
    private String userId;
    private boolean connected = false;

    private String redActive = null;
    private String orangeActive = null;

    @FXML
    public void initialize() {
        mqttClient = new ShayaMqttClient(
                this::onAlertReceived,
                this::onMessageReceived,
                this::onCancelReceived
        );

        setUiDisconnected();
    }

    // ------------------ BOTÓN CONECTAR ------------------
    @FXML
    private void onConnectClicked() {
        if (!connected) {
            userId = userIdField.getText().trim();
            if (userId.isEmpty()) {
                log("SISTEMA", "Ingresa un ID de usuario.");
                return;
            }

            mqttClient.connect(userId);
            connected = true;
            log("SISTEMA", "Conectado como " + userId);
            setUiConnected();

        } else {
            mqttClient.disconnect();
            connected = false;
            log("SISTEMA", "Desconectado.");
            setUiDisconnected();
        }
    }

    // ------------------ ALERTA ROJA ------------------
    @FXML
    private void onSendRedClicked() {
        if (!connected) return;

        redActive = userId;
        mqttClient.sendRedAlert(userId);
        log("YO", "NECESITO AYUDA URGENTE! Alerta roja iniciada.");
        refreshUiState();
    }

    // ------------------ ALERTA NARANJA ------------------
    @FXML
    private void onSendOrangeClicked() {
        if (!connected) return;

        orangeActive = userId;
        mqttClient.sendOrangeAlert(userId);
        log("YO", "AUXILIO! Alerta naranja iniciada.");
        refreshUiState();
    }

    // ------------------ CANCELAR ALERTA ------------------
    @FXML
    private void onCancelClicked() {
        if (!connected) return;

        boolean isMyOrange = (orangeActive != null && orangeActive.equals(userId));
        boolean isMyRed = (redActive != null && redActive.equals(userId));

        boolean cancelOrange = isMyOrange && !isMyRed;

        mqttClient.sendCancelAlert(userId, cancelOrange);

        redActive = null;
        orangeActive = null;

        log("YO", "He cancelado la alerta.");
        refreshUiState();
    }

    // ------------------ ENVIAR MENSAJE NARANJA ------------------
    @FXML
    private void onSendMessageClicked() {
        if (!connected) return;

        String text = messageField.getText().trim();
        if (text.isEmpty()) return;

        mqttClient.sendOrangeMessage(userId, text);
        log("YO", text + " [mensaje naranja]");
        messageField.clear();
    }

    // ------------------ CALLBACKS DESDE MQTT ------------------

    private void onAlertReceived(String sender, String type) {
        if ("ROJA".equalsIgnoreCase(type)) {
            redActive = sender;
        } else {
            orangeActive = sender;
        }

        log(sender, "ha activado alerta " + type);
        refreshUiState();
    }

    private void onMessageReceived(String sender, String msg) {
        log(sender, msg + " [mensaje naranja]");
    }

    private void onCancelReceived() {
        redActive = null;
        orangeActive = null;
        log("SISTEMA", "Se ha cancelado la alerta.");
        refreshUiState();
    }

    // ------------------ UI ------------------

    private void refreshUiState() {
        // Fondo según alerta activa (si no soy yo)
        String color = "#242424"; // default

        if (redActive != null && !redActive.equals(userId)) {
            color = "#631c1c";
        } else if (orangeActive != null && !orangeActive.equals(userId)) {
            color = "#883a1b";
        }

        bgPane.setStyle("-fx-background-color: " + color + ";");

        boolean iAmUnderAlert =
                (redActive != null && redActive.equals(userId)) ||
                        (orangeActive != null && orangeActive.equals(userId));

        redButton.setDisable(!connected || iAmUnderAlert);
        orangeButton.setDisable(!connected || iAmUnderAlert);
        cancelButton.setDisable(!connected || !iAmUnderAlert);

        boolean canSendMsg = connected && orangeActive != null && orangeActive.equals(userId);
        messageField.setDisable(!canSendMsg);
        sendMessageButton.setDisable(!canSendMsg);
    }

    private void setUiConnected() {
        userIdField.setDisable(true);
        connectButton.setText("Desconectar");

        redButton.setDisable(false);
        orangeButton.setDisable(false);
        cancelButton.setDisable(true);

        messageField.setDisable(true);
        sendMessageButton.setDisable(true);

        bgPane.setStyle("-fx-background-color: #242424;");
    }

    private void setUiDisconnected() {
        userIdField.setDisable(false);
        connectButton.setText("Conectar");

        redButton.setDisable(true);
        orangeButton.setDisable(true);
        cancelButton.setDisable(true);

        messageField.setDisable(true);
        sendMessageButton.setDisable(true);

        redActive = null;
        orangeActive = null;

        bgPane.setStyle("-fx-background-color: #242424;");
    }

    private void log(String sender, String text) {
        logArea.appendText(sender + ": " + text + "\n");
    }
}
