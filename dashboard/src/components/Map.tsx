import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from "react-leaflet";
import type { Alert } from "../types";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";

interface MapProps {
  orangeAlerts: Alert[];
  redAlerts: Alert[];
}

interface Coords {
  lat: number;
  lon: number;
}

function Map(props: MapProps) {
  const center: [number, number] = [-2.90055, -79.00453];

  return (
    <div className="w-full h-full border border-gray-400">
      <MapContainer center={center} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {props.redAlerts.length > 0 && <ReCenterMap lat={props.redAlerts[0].lat} lon={props.redAlerts[0].lon} />}
        {props.orangeAlerts.length > 0 && (
          <ReCenterMap lat={props.orangeAlerts[0].lat} lon={props.orangeAlerts[0].lon} />
        )}
        {props.orangeAlerts.map((alert, i) => (
          <CircleMarker
            key={`orange-${alert.timestamp}-${i}`}
            center={[alert.lat, alert.lon]}
            pathOptions={{ color: "oklch(70.5% 0.213 47.604)", fillColor: "oklch(75% 0.183 55.934)" }}
            radius={8}
            fillOpacity={0.6}
          >
            <Popup>
              <div>
                {alert.type === "red" && <p>Alerta Roja</p>}
                {alert.type === "orange" && <p>Alerta Naranja</p>}
                <p>Mensaje: {alert.message}</p>
                <p>Timestamp: {alert.timestamp}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
        {props.redAlerts.map((alert, i) => (
          <CircleMarker
            key={`orange-${alert.timestamp}-${i}`}
            center={[alert.lat, alert.lon]}
            pathOptions={{ color: "oklch(63.7% 0.237 25.331)", fillColor: "oklch(70.4% 0.191 22.216)" }}
            radius={8}
            fillOpacity={0.6}
          >
            <Popup>
              <div>
                {alert.type === "red" && <p>Alerta Roja</p>}
                {alert.type === "orange" && <p>Alerta Naranja</p>}
                <p>Mensaje: {alert.message}</p>
                <p>Timestamp: {alert.timestamp}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}

function ReCenterMap({ lat, lon }: Coords) {
  const map = useMap();

  useEffect(() => {
    map.flyTo([lat, lon], map.getZoom());
  }, [lat, lon, map]);

  return null;
}

export default Map;
