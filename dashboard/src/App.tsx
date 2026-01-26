import { useEffect, useState } from "react";
import "./App.css";
import Card from "./components/Card";
import { socket } from "./services/notifications";
import type { Alert } from "./types";
import { motion } from "framer-motion";
import Map from "./components/Map";

function App() {
  const [redAlerts, setRedAlerts] = useState<Alert[]>([]);
  const [orangeAlerts, setOrangeAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    socket.on("red-alert", (data: Alert) => {
      setRedAlerts((prev) => [data, ...prev]);
    });

    socket.on("orange-alert", (data: Alert) => {
      setOrangeAlerts((prev) => [data, ...prev]);
    });

    return () => {
      socket.off("red-alert");
      socket.off("orange-alert");
    };
  });

  return (
    <>
      <div className="p-8 w-dvw h-dvh flex flex-col gap-4 bg-gray-200 overflow-hidden">
        <h2 className="text-2xl font-bold text-center flex-none">MiniShaya</h2>
        <div className="grid grid-cols-12 gap-2 flex-1 min-h-0">
          <div className="col-span-12 lg:col-span-4 flex flex-col gap-2 h-full overflow-hidden">
            <Card className="bg-white flex-1 min-h-0 border border-gray-400" title="Alertas Rojas">
              <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-4">
                {redAlerts.map((alert, i) => (
                  <motion.div
                    key={`${alert.timestamp}-${i}`}
                    layout
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  >
                    <RedAlert data={alert} key={`${alert.timestamp}-${i}`}></RedAlert>
                  </motion.div>
                ))}
              </div>
            </Card>
            <Card className="bg-white flex-1 min-h-0 border border-gray-400" title="Alertas Naranja">
              <div className="flex flex-col gap-2 overflow-y-auto flex-1 pr-4">
                {orangeAlerts.map((alert, i) => (
                  <motion.div
                    key={`${alert.timestamp}-${i}`}
                    layout
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  >
                    <OrangeAlert data={alert}></OrangeAlert>
                  </motion.div>
                ))}
              </div>
            </Card>
          </div>
          <div className="col-span-12 lg:col-span-8 flex-1 min-h-0">
            <Map orangeAlerts={orangeAlerts} redAlerts={redAlerts}></Map>
          </div>
        </div>
      </div>
    </>
  );
}

interface AlertProps {
  data: Alert;
}

function RedAlert(props: AlertProps) {
  return (
    <Card className="bg-red-100 text-red-800">
      <div className="flex flex-col">
        <span className="text-red-400">{new Date(props.data.timestamp).toString()}</span>
        <span>
          <b>Alerta Roja</b> — {props.data.sender} necesita ayuda
        </span>
        <span>
          Mensaje: <i>"{props.data.message}"</i>
        </span>
      </div>
    </Card>
  );
}

function OrangeAlert(props: AlertProps) {
  return (
    <Card className="bg-orange-100 text-orange-800">
      <div className="flex flex-col">
        <span className="text-orange-400">{new Date(props.data.timestamp).toString()}</span>
        <span>
          <b>Alerta Naranja</b> — {props.data.sender} necesita ayuda
        </span>
        <span>
          Mensaje: <i>"{props.data.message}"</i>
        </span>
      </div>
    </Card>
  );
}

export default App;
