import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const powerOutageStore = defineStore('powerOutage', () => {
  const neighborhoodsNoPower = ref<string[]>([])
  const stillNoPower = ref<string[]>([])
  const currentResolveIndex = ref(0)

  const doReport = (neighborhood: string) => {
    if (!neighborhoodsNoPower.value.includes(neighborhood)) {
      neighborhoodsNoPower.value.push(neighborhood)
    }
    if (!stillNoPower.value.includes(neighborhood)) {
      setTimeout(() => {
        stillNoPower.value.push(neighborhood)

        currentResolveIndex.value = stillNoPower.value.length - 1
      }, 10000)
    }
  }

  const fixIndexResolve = (districtName: string) => {
    const index = stillNoPower.value.indexOf(districtName)
    if (index !== -1) stillNoPower.value.splice(index, 1)

    const globalIndex = neighborhoodsNoPower.value.indexOf(districtName)
    if (globalIndex !== -1) neighborhoodsNoPower.value.splice(globalIndex, 1)

    if (currentResolveIndex.value >= stillNoPower.value.length) {
      currentResolveIndex.value = Math.max(0, stillNoPower.value.length - 1)
    }
  }

  const nextResolve = () => {
    if (stillNoPower.value.length > 1) {
      currentResolveIndex.value = (currentResolveIndex.value + 1) % stillNoPower.value.length
    }
  }

  return {
    neighborhoodsNoPower,
    stillNoPower,
    currentResolveIndex,
    doReport,
    fixIndexResolve,
    nextResolve,
    resolveNeighborhoodName: computed(() => stillNoPower.value[currentResolveIndex.value] || ''),
  }
})
