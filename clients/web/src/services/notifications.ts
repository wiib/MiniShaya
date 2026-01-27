import { io } from "socket.io-client";

const NOTIFIER_URL = "http://192.168.49.2:30050";

export const socket = io(NOTIFIER_URL);
