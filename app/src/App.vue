<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { mapBuildStore } from './stores/map'

import ReportPanel from './components/reports/ReportPanel.vue'
import ResolveReportCard from './components/reports/ResolveReportCard.vue'
import PowerOutageList from './components/reports/PowerOutageList.vue'
import MapContainer from './components/map/MapContainer.vue'
import ChatPanel from './components/chat/ChatPanel.vue'
import AdsModal from './components/common/AdsModal.vue'

const mapStore = mapBuildStore()

const showAds = ref(false)
const latestReportedNeighborhood = ref('')

const openChat = ref(false)
const openMenu = ref(false)

const handleReportAdded = (neightborhood: string) => {
  latestReportedNeighborhood.value = neightborhood
  showAds.value = true
}


</script>

<style lang="scss">
@use './assets/styles/App.scss';
</style>

<template>
  <div class="above-content">
    <div class="box-news">
      <h1 class="placard-h1">Notícias sobre falta de luz aparecerão aqui!</h1>
    </div>
  </div>
  <div class="below-content">
    <MapContainer />

    <ReportPanel
      :neighborhood-list="mapStore.neighborhoodsList"
      @report-added="handleReportAdded"
    />

    <PowerOutageList v-model:open-menu="openMenu" />

    <ChatPanel v-model:open-chat="openChat" :open-menu="openMenu" />

    <ResolveReportCard />

    <AdsModal
      :show="showAds"
      :latest-reported-neighborhood="latestReportedNeighborhood"
      @close="showAds = false"
    />
  </div>
</template>
