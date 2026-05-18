import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAccountStore } from './auth'



export const chatFuncStore = defineStore('chat', () => {
  const authStore = authAccountStore()
  const activeTab = ref<'chat' | 'profile' | 'online'>('chat')
  const messages = ref([{ user: 'Usuário', text: 'Bom dia.' }])
  const newMessage = ref('')
  const onlineUsers = computed(() => {
    const list = [
      { name: 'Visitante_Alpha', location: 'Bela Vista' },
      { name: 'Visitante_Beta', location: 'Centro Histórico' },
    ]
    if(authStore.currentUser?.nome)
    { 
      list.push({name: authStore.currentUser?.nome, location: authStore.currentUser?.bairro_criacao})
    }
    return list
  })

  const sendMessages = () => {
    if (newMessage.value.trim()) {
      messages.value.push({
        user: authStore.currentUser?.nome || 'Usuário',
        text: newMessage.value,
      })
      newMessage.value = ''
    }
  }

  const setActiveTab = (tab: 'chat' | 'profile' | 'online') => {
    activeTab.value = tab
  }

  return { activeTab, messages, newMessage, onlineUsers, sendMessages, setActiveTab }
})
