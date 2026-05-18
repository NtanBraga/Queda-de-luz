import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserAccount, UserLogin } from '@/scripts/user/userGeneric'
import { giveAccountInfo, restoreByToken } from '@/scripts/user/authLogin'

export const authAccountStore = defineStore('auth', () => {
  const currentUser = ref<UserAccount | null>(null)
  const isLoggedIn = ref(false)
  const isLoading = ref(false)

  const login = async (credentials: UserLogin) => {
    isLoggedIn.value = true
    try {
      const { account } = await giveAccountInfo(credentials)

      currentUser.value = account
      isLoggedIn.value = true

      console.log(`Login realizado no nome de ${account.nome}`)

      return account
    } catch (e) {
      console.error('Erro ao realizar login: ', e)
      throw e
    } finally {
      isLoading.value = true
    }
  }

  const logout = () => {
    currentUser.value = null
    isLoggedIn.value = false
    localStorage.removeItem('userToken')
  }

  const restoreSession = async () => {
    const token = localStorage.getItem('userToken')
    if (!token) return false

    isLoading.value = true

    try {
      const { account } = await restoreByToken(token)

      currentUser.value = account
      isLoggedIn.value = true

      console.log('Sessão restaurada com sucesso.')
      return true
    } catch (e) {
      console.error('Erro ao restaurar conta: ', e)
      localStorage.removeItem('userToken')
      throw e
    }
  }

  restoreSession()
  return { currentUser, isLoggedIn, isLoading, login, logout, restoreSession }
})
