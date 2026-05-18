<script setup lang="ts">
import { chatFuncStore } from '@/stores/chat'
import { authAccountStore } from '@/stores/auth'
import ChatMessages from './ChatMessages.vue'
import OnlineUsers from './OnlineUsers.vue'
import ProfileView from './ProfileView.vue'

const chatStore = chatFuncStore()
const authStore = authAccountStore()

const openChat = defineModel<boolean>('openChat', { default: true })

defineProps<{
  openMenu: boolean
}>()
</script>

<template>
  <div class="box-chat" :class="{ isHidden: !openChat }">
    <div class="box-chat-header">
      <div class="box-chat-verify-logged">
        <div class="box-chat-profile-image" :class="{ 'is-logged': authStore.isLoggedIn }">
          <img src="../../assets/images/no-photo.svg" />
        </div>
        <div class="box-chat-toggle-profile-online">
          <span
            class="button-switch-profile"
            @click="chatStore.setActiveTab(chatStore.activeTab === 'profile' ? 'chat' : 'profile')"
            >{{
              chatStore.activeTab === 'profile'
                ? 'Voltar ao chat'
                : authStore.isLoggedIn
                  ? 'Meu perfil'
                  : 'Entrar / Cadastro'
            }}</span
          >
          <span
            v-if="authStore.isLoggedIn"
            :class="{ 'is-active': chatStore.activeTab === 'online' }"
            class="button-switch-online"
            @click="chatStore.setActiveTab(chatStore.activeTab === 'online' ? 'chat' : 'online')"
          >
            {{
              chatStore.activeTab === 'online'
                ? 'Fechar Lista'
                : `${chatStore.onlineUsers.length} usuarios online`
            }}
          </span>
        </div>
      </div>
      <button class="box-chat-button" @click="openChat = false">X</button>
    </div>
    <div class="box-chat-content">
      <Transition name="slide" mode="out-in">
        <ChatMessages v-if="chatStore.activeTab === 'chat'" :messages="chatStore.messages" />
        <ProfileView v-else-if="chatStore.activeTab === 'profile'" />
        <OnlineUsers v-else-if="chatStore.activeTab === 'online'" :users="chatStore.onlineUsers" />
      </Transition>
    </div>
  </div>
  <button
    v-if="!openChat"
    @click="openChat = true"
    class="button-chat-outside"
    :class="{ 'shift-to-side': openMenu }"
  >
    <img src="../../assets/images/chat.svg" />
  </button>
</template>
