<script setup lang="ts">
import { powerOutageStore } from '@/stores/powerOutage'
import { computed } from 'vue'

const powerStore = powerOutageStore()

const openMenu = defineModel<boolean>('openMenu', { default: true })

const scheduledNeighborhoods = computed(() => {
  if (!powerStore.scheduledOutages) return []
  return powerStore.scheduledOutages.filter((n) => !powerStore.neighborhoodsNoPower.includes(n))
})

const formatName = (name: string) => {
  if (!name) return ''

  const except = ['de', 'da', 'do', 'das', 'dos', 'e']

  return name
    .toLowerCase()
    .split(' ')
    .map((word, index) => {
      if (index !== 0 && except.includes(word)) {
        return word
      }
      return word.charAt(0).toUpperCase() + word.slice(1)
    })
    .join(' ')
}
</script>

<template>
  <div class="box-power-outage" :class="{ 'is-hidden': !openMenu }">
    <div class="box-power-outage-header">
      <h2 class="box-power-outrage-h2">Bairros sem luz</h2>
      <button class="button-power-outage-inside" @click="openMenu = false">X</button>
    </div>
    <ul class="lista-bairros-sem-luz">
      <li
        v-if="powerStore.neighborhoodsNoPower.length === 0 && scheduledNeighborhoods.length === 0"
        class="lista-items-bairros-sem-luz status-safe"
      >
        <strong>Nenhum bairro reportado</strong>
      </li>
      <li
        v-for="n in powerStore.neighborhoodsNoPower"
        :key="n"
        class="lista-items-bairros-sem-luz status-alert"
      >
        <strong>{{ formatName(n) }}</strong>
        <span
          class="lista-items-bairros-sem-luz-report-badge status-alert"
          v-if="powerStore.reportCount[n]"
        >
          {{ powerStore.reportCount[n] }}
          {{ powerStore.reportCount[n] > 1 ? 'reportes' : 'reporte' }}
        </span>
      </li>
      <li
        v-for="n in scheduledNeighborhoods"
        :key="n"
        class="lista-items-bairros-sem-luz status-scheduled"
      >
        <strong>{{ formatName(n) }}</strong>
        <span class="lista-items-bairros-sem-luz-report-badge status-scheduled"> Manutenção </span>
      </li>
    </ul>
  </div>
  <button v-if="!openMenu" @click="openMenu = true" class="button-power-outage-outside">
    <img src="../../assets/images/light_bulb.svg" />
  </button>
</template>
