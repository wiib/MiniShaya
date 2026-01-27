<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import { Map, TileLayer, Marker, Popup } from "sveaflet";

  import { socket } from "./services/notifications";

  let userName = $state("");
  let userNameLocked = $state(false);

  let initialMessage = $state("");

  let receivedAlert: any = $state();

  const PRODUCER_URL = "http://192.168.49.2:30051";

  onMount(() => {
    socket.on("red-alert", (data) => {
      receivedAlert = data;
    });

    socket.on("orange-alert", (data) => {
      receivedAlert = data;
    });
  });

  onDestroy(() => {
    socket.off("red-alert");
    socket.off("orange-alert");
  });

  function disableName() {
    userNameLocked = true;
  }

  async function redAlert() {
    if (!userName || !initialMessage) return;

    try {
      const response = await fetch(`${PRODUCER_URL}/alert/red`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: initialMessage, sender_id: userName }),
      });

      if (!response.ok) throw new Error("Error al enviar la alerta roja");

      initialMessage = "";
    } catch (err) {
      if (err instanceof Error) console.error(err);
    }
  }

  async function orangeAlert() {
    if (!userName || !initialMessage) return;

    try {
      const response = await fetch(`${PRODUCER_URL}/alert/orange`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: initialMessage, sender_id: userName }),
      });

      if (!response.ok) throw new Error("Error al enviar la alerta naranja");

      initialMessage = "";
    } catch (err) {
      if (err instanceof Error) console.error(err);
    }
  }

  function shouldShowAlert(alert: any) {
    if (alert.sender == userName) return false;
    if (alert.target !== userName) return false;

    return true;
  }
</script>

<main class="p-8 w-dvw h-dvh flex flex-col gap-4 bg-gray-200">
  <h2 class="text-2xl font-bold text-center">Cliente MiniShaya</h2>
  <div class="grid grid-cols-12 gap-4">
    <div class="col-span-12 lg:col-span-4 mb-auto">
      <div
        class="bg-white rounded-xl p-4 flex flex-col gap-2 shadow-md mb-2 border border-gray-400"
      >
        <h3 class="text-xl font-bold text-center mb-4">Usuario</h3>
        <div class="flex flex-row gap-2">
          <input
            type="text"
            name="name"
            id="name"
            class="grow p-2 border border-gray-300 rounded-md"
            placeholder="Nombre"
            disabled={userNameLocked}
            bind:value={userName}
          />
          <button
            class="bg-green-400 hover:bg-green-300 rounded-md p-2 w-16 cursor-pointer"
            disabled={userNameLocked}
            onclick={disableName}
          >
            Fijar
          </button>
        </div>
      </div>
      <div
        class="bg-white rounded-xl p-4 flex flex-col gap-2 shadow-md mb-2 border border-gray-400"
      >
        <h3 class="text-xl font-bold text-center mb-4">Enviar Alerta</h3>
        <input
          type="text"
          name="initialMessage"
          id="initialMessage"
          class="grow p-2 border border-gray-300 rounded-md"
          placeholder="Mensaje inicial"
          bind:value={initialMessage}
        />
        <button
          class="bg-red-400 hover:bg-red-300 rounded-md p-2 font-bold cursor-pointer"
          onclick={redAlert}
        >
          Alerta Roja
        </button>
        <button
          class="bg-orange-400 hover:bg-orange-300 rounded-md p-2 font-bold cursor-pointer"
          onclick={orangeAlert}
        >
          Alerta Naranja
        </button>
      </div>
    </div>
  </div>
  {#if receivedAlert && shouldShowAlert(receivedAlert)}
    <div class="col-span-12 lg:col-span-8 bg-white rounded-xl p-4 flex flex-col gap-2 shadow-md">
      <h3 class="text-xl font-bold text-center mb-4">Alerta Recibida</h3>
      <div class="flex flex-row justify-between">
        <span class="font-bold">Tipo:</span>
        <span>{receivedAlert.type === "red" ? "ROJA" : "NARANJA"}</span>
      </div>
      <div class="flex flex-row justify-between">
        <span class="font-bold">Emisor:</span>
        <span>{receivedAlert.sender}</span>
      </div>
      <div class="flex flex-row justify-between">
        <span class="font-bold">Mensaje:</span>
        <span>{receivedAlert.message}</span>
      </div>
      <span class="font-bold text-center">Ubicación</span>
      <div style="width: 100%; height: 500px">
        <Map options={{ center: [receivedAlert.lat, receivedAlert.lon], zoom: 15 }}>
          <TileLayer url={"https://tile.openstreetmap.org/{z}/{x}/{y}.png"} />
          <Marker latLng={[receivedAlert.lat, receivedAlert.lon]} />
        </Map>
      </div>
    </div>
  {/if}
</main>

<style>
</style>
