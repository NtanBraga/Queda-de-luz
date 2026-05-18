<script setup lang="ts">
import { onMounted, onUnmounted, watch, ref } from 'vue'
import { initMap } from '@/scripts/maps/map'
import {
  neighborhoodOutlines,
  clearAllPolygons,
  fetchAllNeighborhoods,
} from '@/scripts/maps/neighborhoodMap'
import { mapBuildStore } from '@/stores/map'
import { powerOutageStore } from '@/stores/powerOutage'
import { storeToRefs } from 'pinia'

const mapStore = mapBuildStore()
const powerStore = powerOutageStore()

const isMapReady = ref(false)

const { initiateMap, neighborhoodsList, city, detectLocation } = storeToRefs(mapStore)
const { neighborhoodsNoPower } = storeToRefs(powerStore)

const loadMap = async () => {
  try {
    isMapReady.value = false
    const mapDiv = document.getElementById('map-canvas')
    if (mapDiv) mapDiv.innerHTML = ''

    initiateMap.value = await initMap('map-canvas', city.value, neighborhoodsNoPower.value)
    
    if (neighborhoodsNoPower.value.length > 0 && initiateMap.value) {
      await neighborhoodOutlines(initiateMap.value, neighborhoodsNoPower.value, city.value, false)
    }
    isMapReady.value = true
    console.log(`Mapa de ${city.value} foi carregado com sucesso.`)
  } catch (e) {
    console.error('Errp ap carregar o mapa: ', e)
    isMapReady.value = true
  }
}

watch(
  () => neighborhoodsNoPower.value,
  async (newList) => {
    if (!initiateMap.value && !isMapReady.value) return
    
    clearAllPolygons()

    if(newList.length > 0) {
      await neighborhoodOutlines(initiateMap.value!, newList, city.value, false)
    }

  },
  { deep: true },
)

const handleLocationDetected = async (e: any) => {
  const { neighborhood, city: newCity } = e.detail

  const strictCity = city.value !== ''


  if (!strictCity && newCity && newCity !== city.value) {
    console.warn(`Mudança de cidade: ${city.value} -> ${newCity}`)
    city.value = newCity

    neighborhoodsList.value = await fetchAllNeighborhoods(newCity)

    await loadMap()
  }else if(strictCity){
    if(newCity === city.value){
      detectLocation.value = neighborhood
    }else{
      detectLocation.value = 'Fora de area'
    }
    
  }
  
}

const handleDetected = (e: any) => (detectLocation.value = e.detail.name)

const handleMapClick = (e: any) => {
  const { name, city: clickedCity } = e.detail


  if (clickedCity && clickedCity !== city.value) {
    console.warn('Clique fora da cidade atual.') 
    return
  }

  mapStore.isSearching = false
  mapStore.setSelectedNeighborhood(name)
  console.log(`Bairro clicado no mapa: ${name}`)
}

const setupMapEvents = () => {
  window.addEventListener('location-detected', handleLocationDetected)
  window.addEventListener('neighborhood-detected', handleDetected)
  window.addEventListener('map-neighborhood-clicked', handleMapClick)
  window.addEventListener('map-neighborhood-loading', () => { mapStore.isSearching = true})
}

onMounted(async () => {
  setupMapEvents()

  if (neighborhoodsList.value.length === 0) {
    neighborhoodsList.value = await fetchAllNeighborhoods(city.value)
  }
  await loadMap()
})

onUnmounted(() => {
  window.removeEventListener('location-detected', handleLocationDetected)
  window.removeEventListener('neighborhood-detected', handleDetected)
  window.removeEventListener('map-neighborhood-clicked', handleMapClick)
  window.removeEventListener('map-neighborhood-loading', () => { mapStore.isSearching = true})
})
</script>

<template>
  <div class="box-map" id="map-canvas"></div>
  <div v-if="!isMapReady" class="box-map-loading">
    <div class="box-map-spinner"></div>
    <span class="box-map-loading-text">Carregando mapa...</span>
  </div>
</template>
