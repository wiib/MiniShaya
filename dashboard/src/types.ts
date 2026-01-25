export interface Alert {
  type: "orange" | "red";
  message: string;
  sender: string;
  timestamp: string;
  lat: number;
  lon: number;
}
