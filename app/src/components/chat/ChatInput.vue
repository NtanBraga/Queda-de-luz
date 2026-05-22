<script setup lang="ts">
const modelValue = defineModel<string>()

const emit = defineEmits<{
  send: []
}>()

const send = () => {
  emit('send')
}
</script>

<template>
  <div class="box-chat-input">
    <input
      v-model="modelValue"
      type="text"
      placeholder="Digite algo..."
      aria-label="Escreva sua mensagem para o chat"
      @keyup.enter="send"
    />
    <button @click="send" aria-label="Enviar mensagem">➤</button>
  </div>
</template>
