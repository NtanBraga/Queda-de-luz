<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { initMap } from './scripts/map.ts'

const openMenu = ref(true)
const openChat = ref(true)
const newMessage = ref('')

const activeTab = ref('chat')

const loggedUser = ref(false)

const messages = ref([{ user: 'Test', text: 'Mensagem de teste.' }])

const toggleProfileChatView = () => {
  activeTab.value = activeTab.value === 'chat' ? 'profile' : 'chat'
}

const sendMessage = () => {
  if (newMessage.value.trim()) {
    messages.value.push({
      user: 'Usuario',
      text: newMessage.value,
    })
    newMessage.value = ''

    setTimeout(() => {
      const chatContainer = document.querySelector('.box-chat-messages')
      if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight
    }, 50)
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
    <div class="box-chat" :class="{ isHidden: !openChat }">
      <div class="box-chat-header">
        <div class="box-chat-verify-logged" @click="toggleProfileChatView">
          <div class="box-chat-profile-image" :class="{ 'is-logged': loggedUser}"></div>
          <span class="box-chat-islogged-text">{{
            activeTab === 'chat' ? (loggedUser ? 'Meu perfil' : 'Entrar / Cadastro') : 'Voltar ao chat'
          }}</span>
        </div>
        <button class="box-chat-button" @click="openChat = false">X</button>
      </div>
      <div class="box-chat-content">
        <Transition name="slide" mode="out-in">
          <div v-if="activeTab === 'chat'" key="chat" class="box-chat-viewchat">
            <div class="box-chat-messages">
              <div v-for="(msg, index) in messages" :key="index" class="message">
                <strong>{{ msg.user }}: </strong>{{ msg.text }}
              </div>
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
          <div v-else key="profile" class="box-chat-viewprofile">
            <div v-if="!loggedUser" class="box-chat-loginform">
              <h3>Acessar a conta</h3>
              <input type="text" placeholder="E-mail">
              <input type="password" placeholder="Senha">
              <button class="box-chat-loginform-button" @click="loggedUser = true">ENTRAR</button>
            </div>
            <div v-else class="box-chat-profile-table-container">
              <table class="box-chat-profile-table">
                <thead>
                  <tr><th colspan="2">Dados do usuário</th></tr>
                </thead>
                <tbody>
                  <tr><td>Nome:</td><td> Visitante Teste</td></tr>
                  <tr><td>Localização:</td><td> Porto Alegre, RS</td></tr>
                  <tr><td>Status:</td><td><span class="status-online">Online</span></td></tr>
                  <tr><td>Notificações:</td><td>Ativadas</td></tr>
                </tbody>
              </table>
              <button class="box-chat-viewprofile-logoutbutton" @click="loggedUser = false">Sair da conta</button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>
