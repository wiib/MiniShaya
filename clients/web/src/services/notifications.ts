import { io } from "socket.io-client";

const NOTIFIER_URL = "http://localhost:3001";

export const socket = io(NOTIFIER_URL);
