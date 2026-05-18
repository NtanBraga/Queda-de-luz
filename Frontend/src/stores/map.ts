import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NeighborhoodInfo } from '@/scripts/maps/neighborhoodMap'

export const mapBuildStore = defineStore('map', () => {
  const city = ref('Porto Alegre')
  const neighborhoodsList = ref<NeighborhoodInfo[]>([])
  const initiateMap = ref<google.maps.Map | undefined>(undefined)
  const detectLocation = ref<string>('')
  const selectedNeighborhood = ref<string>('')
  const isSearching = ref(false)

  const setSelectedNeighborhood = (name: string) => {
    selectedNeighborhood.value = name
  }

  return { city, neighborhoodsList, initiateMap, detectLocation, isSearching, selectedNeighborhood, setSelectedNeighborhood }
})
