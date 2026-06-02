import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const powerOutageStore = defineStore('powerOutage', () => {
  const neighborhoodsNoPower = ref<string[]>([])
  const stillNoPower = ref<string[]>([])
  const currentResolveIndex = ref(0)
  const reportCount = ref<Record<string, number>>({})

  const doReport = (neighborhood: string) => {
    reportCount.value[neighborhood] = (reportCount.value[neighborhood] || 0) + 1

    if (reportCount.value[neighborhood] >= 3) {
      if (!neighborhoodsNoPower.value.includes(neighborhood)) {
        neighborhoodsNoPower.value.push(neighborhood)
      }
    }

    if (!stillNoPower.value.includes(neighborhood)) {
      setTimeout(() => {
        stillNoPower.value.push(neighborhood)
        if (stillNoPower.value.length === 1) {
          currentResolveIndex.value = 0
        }
      }, 10000)
    }
  }

  const fixIndexResolve = (districtName: string) => {
    const index = stillNoPower.value.indexOf(districtName)
    if (index !== -1) stillNoPower.value.splice(index, 1)

    const globalIndex = neighborhoodsNoPower.value.indexOf(districtName)
    if (globalIndex !== -1) neighborhoodsNoPower.value.splice(globalIndex, 1)
    delete reportCount.value[districtName]

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
    reportCount,
    doReport,
    fixIndexResolve,
    nextResolve,
    resolveNeighborhoodName: computed(() => stillNoPower.value[currentResolveIndex.value] || ''),
  }
})
