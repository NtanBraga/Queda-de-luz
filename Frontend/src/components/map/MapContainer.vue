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
import { requestUserLocation, fetchAllLocation } from '@/scripts/maps/userLocation'
import { getReports } from '@/scripts/user/reports'

const CACHED_KEYS = {
  CITY: 'user_selected_city',
  LAT: 'user-lat',
  LNG: 'user-lng',
}

const mapStore = mapBuildStore()
const powerStore = powerOutageStore()

const isMapReady = ref(false)

const loadReports = async () => {
  try {
    const data = await getReports()

    console.log('DADOS CRUS DA API (GET):', data)

    if (data && data.districts_Data) {
      const reportedNames: string[] = []
      const counts: Record<string, number> = {}

      Object.values(data.districts_Data).forEach((district: any) => {
        const districtName = district.district_Name

        const statistic = district.district_Statistics

        if (statistic && Array.isArray(statistic)) {
          const powerOutageStat = statistic.find((stat: any) => stat.problem_Category_Id === 1)

          if (powerOutageStat && powerOutageStat.reported_Amount > 0) {
            reportedNames.push(districtName)
            counts[districtName] = powerOutageStat.reported_Amount
          }
        }
      })
      powerStore.neighborhoodsNoPower = reportedNames
      powerStore.reportCount = counts

      console.log(
        `Sincronizando dados: ${reportedNames.length} bairros reportados em ${mapStore.city}`,
      )
    }
  } catch (e) {
    console.error('Erro ao tentar carregar reportes: ', e)
  }
}

const loadMap = async (targetCity: string, lat?: number, lng?: number) => {
  try {
    isMapReady.value = false

    if (mapStore.neighborhoodsList.length === 0 || mapStore.city !== targetCity) {
      mapStore.neighborhoodsList = await fetchAllNeighborhoods(targetCity)
    }

    mapStore.city = targetCity

    localStorage.setItem(CACHED_KEYS.CITY, targetCity)
    if (lat !== undefined && lng !== undefined) {
      localStorage.setItem(CACHED_KEYS.LAT, lat.toString())
      localStorage.setItem(CACHED_KEYS.LNG, lng.toString())
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

    await loadReports()

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
    if (!mapStore.initiateMap && !isMapReady.value) return

    clearAllPolygons()

    if (newList.length > 0) {
      await neighborhoodOutlines(mapStore.initiateMap!, newList, mapStore.city, false)
    }
  },
  { deep: true },
)

// Se verificado uma cidade nova, ele é redirecionado
const handleLocationDetected = async (e: any) => {
  const { neighborhood, city: newCity } = e.detail

  if (newCity === mapStore.city) {
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

const setupMapEvents = () => {
  window.addEventListener('location-detected', handleLocationDetected)
  window.addEventListener('neighborhood-detected', handleDetected)
  window.addEventListener('map-neighborhood-clicked', handleMapClick)
  window.addEventListener('map-neighborhood-loading', () => {
    mapStore.isSearching = true
  })
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
      }
    } else {
      console.log('Usuário continua na mesma localização. Otimizando renderização.')
    }
  } catch (e) {
    console.warn('Verificação de localização falhou ou negada.')
  }
}

onMounted(async () => {
  setupMapEvents()

  const savedCity = localStorage.getItem(CACHED_KEYS.CITY)
  const savedLat = localStorage.getItem(CACHED_KEYS.LAT)
  const savedLng = localStorage.getItem(CACHED_KEYS.LNG)

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
