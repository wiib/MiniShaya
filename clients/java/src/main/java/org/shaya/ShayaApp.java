package org.shaya;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class ShayaApp extends Application {

    @Override
    public void start(Stage stage) throws Exception {
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/org/shaya/ui.fxml"));
        Parent root = loader.load();

        Scene scene = new Scene(root, 900, 700);
        scene.getStylesheets().add(
                getClass().getResource("/org/shaya/styles.css").toExternalForm()
        );

        stage.setTitle("Cliente SHAYA - Java");
        stage.setScene(scene);
        stage.setResizable(false);
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
