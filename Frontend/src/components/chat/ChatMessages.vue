<script setup lang="ts">
import { chatFuncStore } from '@/stores/chat';
import ChatInput from './ChatInput.vue';

defineProps<{
  messages: Array<{ user: string; text: string }>
}>()

const chatStore = chatFuncStore()

</script>

<template>
  <div class="box-chat-view-chat">
    <div class="box-chat-messages">
      <div v-for="(msg, index) in messages" :key="index" class="message">
        <strong>{{ msg.user }}: </strong>{{ msg.text }}
      </div>
    </div>
    <ChatInput 
      v-model="chatStore.newMessage"
      @send="chatStore.sendMessages"/>
  </div>
</template>
