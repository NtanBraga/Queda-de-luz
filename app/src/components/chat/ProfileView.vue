<script setup lang="ts">
import { authAccountStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const authStore = authAccountStore()
const { currentUser } = storeToRefs(authStore)
</script>

<template>
  <div class="box-chat-viewprofile">
    <div class="box-chat-profile-table-container">
      <div class="box-chat-profile-header">
        <div class="box-chat-profile-avatar">
          <img v-if="currentUser?.imagem_perfil_link" :src="currentUser.imagem_perfil_link" />
          <div v-else class="box-chat-profile-avatar-placeholder">
            <img src="../../assets/images/no-photo.svg" />
          </div>
        </div>
        <div class="box-chat-profile-info">
          <h4 class="box-chat-profile-name">{{ currentUser?.nome }}</h4>
          <p class="box-chat-profile-neighborhood">{{ currentUser?.bairro_criacao }}</p>
        </div>
      </div>
      <div class="box-chat-profile-bio">
        <p class="box-chat-profile-bio-title">Descrição</p>
        <p class="box-chat-profile-bio-text">
          {{ currentUser?.descricao || 'Ainda sem nenhuma descrição.' }}
        </p>
      </div>
      <div v-if="currentUser?.accountType === 'BusinessAccount'" class="box-chat-profile-cnpj-ads">
        <p class="box-chat-profile-cnpj-ads-label">
          Produtos anunciados (Disponiveis: {{ currentUser?.slot_anuncio_quantidade + 2 }})
        </p>
        <div class="box-chat-profile-cnpj-ads-album">
          <div v-for="i in 3" :key="i" class="box-chat-profile-cnpj-slots">
            <span>Placeholder</span>
          </div>
        </div>
      </div>
      <div class="box-chat-profile-buttons-container">
        <button class="box-chat-profile-editbutton">Editar conta</button>
        <button class="box-chat-profile-logoutbutton">Sair da conta</button>
      </div>
    </div>
  </div>
</template>
