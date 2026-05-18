<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { powerOutageStore } from './stores/powerOutage'
import { authAccountStore } from './stores/auth'
import { mapBuildStore } from './stores/map'

import ReportPanel from './components/reports/ReportPanel.vue'
import ResolveReportCard from './components/reports/ResolveReportCard.vue'
import PowerOutageList from './components/reports/PowerOutageList.vue'
import MapContainer from './components/map/MapContainer.vue'
import ChatPanel from './components/chat/ChatPanel.vue'
import AdsModal from './components/common/adsModal.vue'

import { fetchAllNeighborhoods } from './scripts/maps/neighborhoodMap'

const mapStore = mapBuildStore()
const powerStore = powerOutageStore()
const authStore = authAccountStore()

const showAds = ref(false)
const latestReportedNeighborhood = ref('')

const openChat = ref(true)
const openMenu = ref(true)

const handleReportAdded = (neightborhood: string) => {
  latestReportedNeighborhood.value = neightborhood
  showAds.value = true
}

const loadInitialData = async () => {
  try {
    if (mapStore.neighborhoodsList.length === 0) {
      mapStore.neighborhoodsList = await fetchAllNeighborhoods(mapStore.city)
    }
    console.log(`Carregamento inicial realizado.Bairros: ${mapStore.neighborhoodsList.length}`)
  } catch (e) {
    console.error('Eroo ao carregar dados iniciais: ', e)
    throw e
  }
}

onMounted(async () => {
  await loadInitialData()
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
    <ResolveReportCard />

    <AdsModal
      :show="showAds"
      :latest-reported-neighborhood="latestReportedNeighborhood"
      @close="showAds = false"
    />

    <ReportPanel
      :neighborhood-list="mapStore.neighborhoodsList"
      @report-added="handleReportAdded"
    />

    <PowerOutageList v-model:open-menu="openMenu" />

    <MapContainer />

    <ChatPanel v-model:open-chat="openChat" :open-menu="openMenu" />
  </div>
</template>
