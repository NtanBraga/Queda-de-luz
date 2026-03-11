<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { initMap } from './scripts/map.ts'

const openMenu = ref(true)
const openChat = ref(true)
const newMessage = ref('')

const sendMessage = () => {
  if(newMessage.value.trim()) {
    newMessage.value= '';
  }
}


onMounted(async () => {
  await initMap('map-canvas')
})
</script>

<style lang="scss">
@use './assets/styles/App.scss';
</style>

<template>
  <div class="above-content">
    <div class="box-news"><h1 class="placard-h1">News</h1></div>
  </div>
  <div class="below-content">
    <button v-if="!openMenu" @click="openMenu = true" class="button-power-outage-outside">P</button>
    <button v-if="!openChat" @click="openChat = true" class="button-chat-outside"></button>
    <div class="box-power-outage" :class="{ 'is-hidden': !openMenu }">
      <div class="box-power-outage-header">
        <h2 class="box-power-outrage-h2">Bairros sem luz</h2>
        <button class="button-power-outage-inside" @click="openMenu = false">X</button>
      </div>
      <ul class="lista-bairros-sem-luz">
        <li class="lista-items-bairros-sem-luz"><strong>Bairro sem luz 1</strong></li>
        <li class="lista-items-bairros-sem-luz"><strong>Bairro sem luz 2</strong></li>
        <li class="lista-items-bairros-sem-luz"><strong>Bairro sem luz 3</strong></li>
        <li class="lista-items-bairros-sem-luz"><strong>Bairro sem luz 4</strong></li>
        <li class="lista-items-bairros-sem-luz"><strong>Bairro sem luz 5</strong></li>
      </ul>
    </div>
    <div class="box-map" id="map-canvas"><h1>Map</h1></div>
    <div class="box-chat" :class="{ 'isHidden': !openChat}">
      <div class="box-chat-header">
        <h2 class="box-chat-header-h2">
          CHAT COMUNITARIO
        </h2>
        <button class="box-chat-button" @click="openChat = false">X</button>
      </div>
      <div class="box-chat-messages">
        <div class="message"><strong>User:</strong> Ta sem luz</div>
      </div>
      <div class="box-chat-input">
        <input
          v-model="newMessage"
          type="text"
          placeholder="Digite algo..."
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage">➤</button>
      </div>
    </div>
  </div>
</template>
