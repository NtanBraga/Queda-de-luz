import { defineStore } from 'pinia'
import { ref } from 'vue'

export const authAccountStore = defineStore('auth', () => {
  const isLoggedIn = ref(false)

  const currentUser = ref({
    id: 2026,
    nome: 'Conta Protótipa Teste',
    bairro_criacao: 'Bela Vista',
    descricao: 'Está é uma conta feita para protótipo e amostragem.',
    accountType: 'BusinessAccount',
    slot_anuncio_quantidade: 3,
    imagem_perfil_link: '',
  })

  return { currentUser, isLoggedIn }
})
