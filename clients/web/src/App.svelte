<script lang="ts">
</script>

<main class="p-8 w-dvw h-dvh flex flex-col gap-4 bg-gray-200">
  <h2 class="text-2xl font-bold text-center">Cliente MiniShaya</h2>
  <div class="grid grid-cols-12 gap-4">
    <div class="col-span-12 lg:col-span-4 bg-white rounded-xl p-4 flex flex-col gap-2 shadow-md">
      <h3 class="text-xl font-bold text-center mb-4">Enviar Alerta</h3>
      <div class="flex flex-row gap-2">
        <input
          type="text"
          name="name"
          id="name"
          class="grow p-2 border border-gray-300 rounded-md"
          placeholder="Nombre"
        />
        <button class="bg-green-400 rounded-md p-2 w-16">Fijar</button>
      </div>
      <button class="bg-red-400 rounded-md p-2">Alerta Roja</button>
      <button class="bg-orange-400 rounded-md p-2">Alerta Naranja</button>
    </div>
    <div class="col-span-12 lg:col-span-8 bg-white rounded-xl p-4 flex flex-col shadow-md">
      <h3 class="text-xl font-bold text-center mb-4">Chat</h3>
      <div class="flex flex-row gap-2">
        <input
          type="text"
          name="message"
          id="message"
          class="grow p-2 border border-gray-300 rounded-md"
          placeholder="Escribe aquí tu mensaje..."
        />
        <button class="bg-green-400 rounded-md p-2 w-16">Enviar</button>
      </div>
    </div>
  </div>
</main>

<style>
</style>
