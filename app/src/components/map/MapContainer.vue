<script setup lang="ts">
import { onMounted, onUnmounted, watch, ref } from 'vue'
import { initMap } from '@/scripts/maps/initMap'
import {
  neighborhoodOutlines,
  clearAllPolygons,
  fetchAllNeighborhoods,
} from '@/scripts/maps/neighborhoodMap'
import { mapBuildStore } from '@/stores/map'
import { powerOutageStore } from '@/stores/powerOutage'
import { fetchAllLocation, requestUserLocation } from '@/scripts/user/userLocation'

const mapStore = mapBuildStore()
const powerStore = powerOutageStore()

const isMapReady = ref(false)

const showOptions = ref(false)
const isLocating = ref(false)

const loadMap = async (targetCity: string, lat?: number, lng?: number) => {
  try {
    isMapReady.value = false
    showOptions.value = false
    isLocating.value = false

    if (mapStore.neighborhoodsList.length === 0 || mapStore.city !== targetCity) {
      mapStore.neighborhoodsList = await fetchAllNeighborhoods(targetCity)
    }

    mapStore.city = targetCity

    localStorage.setItem('user-selected-city', targetCity)
    if (lat !== undefined && lng !== undefined) {
      localStorage.setItem('user-lat', lat.toString())
      localStorage.setItem('user-lng', lng.toString())
    }

    const mapDiv = document.getElementById('map-canvas')
    if (mapDiv) mapDiv.innerHTML = ''

    mapStore.initiateMap = await initMap(
      'map-canvas',
      targetCity,
      powerStore.neighborhoodsNoPower,
      lat,
      lng,
    )

    isMapReady.value = true
    console.log(`Mapa de ${mapStore.city} foi carregado com sucesso.`)
  } catch (e) {
    console.error('Erro ao carregar o mapa: ', e)
    isMapReady.value = true
  }
}

watch(
  () => powerStore.neighborhoodsNoPower,
  async (newList) => {
    if (!mapStore.initiateMap || !isMapReady.value) return

    clearAllPolygons()

    if (newList.length > 0) {
      await neighborhoodOutlines(mapStore.initiateMap!, newList, mapStore.city, false)
    }
  },
  { deep: true },
)

const handleUseLocation = async () => {
  isLocating.value = true
  showOptions.value = false

  try {
    const coords = await requestUserLocation()
    const locationData = await fetchAllLocation(coords.lat, coords.lng)

    const targetCity = locationData?.city || 'Porto Alegre'
    await loadMap(targetCity, coords.lat, coords.lng)
  } catch (error) {
    loadMap('Porto Alegre')
  }
}
const handleSkipLocation = () => {
  loadMap('Porto Alegre')
}

const handleLocationDetected = async (e: any) => {
  const { neighborhood, city: newCity } = e.detail

  if (newCity && newCity !== mapStore.city && isMapReady.value) {
    console.warn(`Localização ativada posteriormente. Redirecionando para ${newCity}`)
    await loadMap(newCity)
  } else if (newCity === mapStore.city) {
    mapStore.detectLocation = neighborhood
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

const checkUserLocation = async (cachedLat?: number, cachedLng?: number) => {
  try {
    const coords = await requestUserLocation()

    const isNewLocation =
      !cachedLat ||
      !cachedLng ||
      coords.lat.toFixed(3) !== cachedLat.toFixed(3) ||
      coords.lng.toFixed(3) !== cachedLng.toFixed(3)

    if (isNewLocation) {
      console.log('Movimentação detectada. Atualizando posição...')
      const locationData = await fetchAllLocation(coords.lat, coords.lng)

      if (locationData && locationData.city) {
        await loadMap(locationData.city, coords.lat, coords.lng)
      } else {
        console.log('Usuário continua na mesma localização. Otimizando renderização.')
      }
    }
  } catch (e) {
    console.warn('Verificação de localização falhou ou negada.')
  }
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

  const savedCity = localStorage.getItem('user-selected-city')
  const savedLat = localStorage.getItem('user-lat')
  const savedLng = localStorage.getItem('user-lng')

  if (savedCity) {
    mapStore.city = savedCity
  }

  if (mapStore.city && mapStore.city.trim() !== '') {
    const lat = savedLat ? parseFloat(savedLat) : undefined
    const lng = savedLng ? parseFloat(savedLng) : undefined

    await loadMap(mapStore.city, lat, lng)
    await checkUserLocation(lat, lng)
    return
  }
  showOptions.value = true
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
    <div v-if="showOptions" class="box-map-options-overlay">
      <h2>Bem-vindo ao Infralá!</h2>
      <p>
        Queremos mostrar os status de infraestrutura da sua cidade. Recomendamos ativar a sua
        localização!
      </p>

      <div class="box-map-options-btns">
        <button class="box-map-options-btn-primary" @click="handleUseLocation">
          USAR MINHA LOCALIZAÇÃO
        </button>
        <button class="box-map-options-btc-secondary" @click="handleSkipLocation">
          Continuar em Porto Alegre
        </button>
      </div>
    </div>
    <div v-else class="box-map-spinner-container">
      <div class="box-map-spinner"></div>
      <span class="box-map-loading-text">{{
        isLocating ? 'Buscando sua cidade...' : 'Carregando mapa...'
      }}</span>
    </div>
  </div>
</template>
