<script setup lang="ts">
import { ref } from 'vue'
import { powerOutageStore } from '@/stores/powerOutage'

const powerStore = powerOutageStore()

const openMenu = defineModel<boolean>('openMenu', { default: true })

</script>

<template>
  <div class="box-power-outage" :class="{ 'is-hidden': !openMenu }">
    <div class="box-power-outage-header">
      <h2 class="box-power-outrage-h2">Bairros sem luz</h2>
      <button class="button-power-outage-inside" @click="openMenu = false">X</button>
    </div>
    <ul class="lista-bairros-sem-luz">
      <li
        v-if="powerStore.neighborhoodsNoPower.length === 0"
        class="lista-items-bairros-sem-luz status-safe"
      >
        <strong>Nenhum bairro reportado</strong>
      </li>
      <li
        v-for="n in powerStore.neighborhoodsNoPower"
        :key="n"
        class="lista-items-bairros-sem-luz status-alert"
      >
        <strong>{{ n }}</strong>
      </li>
    </ul>
  </div>
  <button v-if="!openMenu" @click="openMenu = true" class="button-power-outage-outside">
    <img src="../../assets/images/light_bulb.svg" />
  </button>
</template>
