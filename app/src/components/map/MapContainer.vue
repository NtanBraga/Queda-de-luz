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

const mapStore = mapBuildStore()
const powerStore = powerOutageStore()

const isMapReady = ref(false)

const loadMap = async () => {
  try {
    isMapReady.value = false
    const mapDiv = document.getElementById('map-canvas')
    if (mapDiv) mapDiv.innerHTML = ''

    mapStore.initiateMap = await initMap(
      'map-canvas',
      mapStore.city,
      powerStore.neighborhoodsNoPower,
    )

    isMapReady.value = true
    console.log(`Mapa de ${mapStore.city} foi carregado com sucesso.`)
  } catch (e) {
    console.error('Errp ao carregar o mapa: ', e)
    isMapReady.value = true
  }
}

watch(
  () => powerStore.neighborhoodsNoPower,
  async (newList) => {
    if (!mapStore.initiateMap && !isMapReady.value) return

    clearAllPolygons()

    if (newList.length > 0) {
      await neighborhoodOutlines(mapStore.initiateMap!, newList, mapStore.city, false)
    }
  },
  { deep: true },
)

const handleLocationDetected = async (e: any) => {
  const { neighborhood, city: newCity } = e.detail

  const strictCity = mapStore.city !== ''

  if (!strictCity && newCity && newCity !== mapStore.city) {
    console.warn(`Mudança de cidade: ${mapStore.city} -> ${newCity}`)
    mapStore.city = newCity

    mapStore.neighborhoodsList = await fetchAllNeighborhoods(newCity)

    await loadMap()
  } else if (strictCity) {
    if (newCity === mapStore.city) {
      mapStore.detectLocation = neighborhood
    } else {
      mapStore.detectLocation = 'Fora de area'
    }
  }
}

const handleDetected = (e: any) => (mapStore.detectLocation = e.detail.name)

const handleMapClick = (e: any) => {
  const { name, city: clickedCity } = e.detail

  if (clickedCity && clickedCity !== mapStore.city) {
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
  window.addEventListener('map-neighborhood-loading', () => {
    mapStore.isSearching = true
  })
}

onMounted(async () => {
  setupMapEvents()

  if (mapStore.neighborhoodsList.length === 0) {
    mapStore.neighborhoodsList = await fetchAllNeighborhoods(mapStore.city)
  }
  await loadMap()
})

onUnmounted(() => {
  window.removeEventListener('location-detected', handleLocationDetected)
  window.removeEventListener('neighborhood-detected', handleDetected)
  window.removeEventListener('map-neighborhood-clicked', handleMapClick)
  window.removeEventListener('map-neighborhood-loading', () => {
    mapStore.isSearching = true
  })
})
</script>

<template>
  <div class="box-map" id="map-canvas"></div>
  <div v-if="!isMapReady" class="box-map-loading">
    <div class="box-map-spinner"></div>
    <span class="box-map-loading-text">Carregando mapa...</span>
  </div>
</template>
