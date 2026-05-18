<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { powerOutageStore } from '@/stores/powerOutage'
import { mapBuildStore } from '@/stores/map'
import { type NeighborhoodInfo } from '@/scripts/maps/neighborhoodMap'

const powerStore = powerOutageStore()
const mapStore = mapBuildStore()

const props = defineProps<{
  neighborhoodList: NeighborhoodInfo[]
}>()

const emit = defineEmits<{
  reportAdded: [neighborhood: string]
  locationSelected: [name: string]
}>()

const putManualLocation = ref('')
const isChangingReport = ref(false)
const searchReportQuery = ref('')

const filteredNeighborhoods = computed(() =>
  props.neighborhoodList.filter((n) =>
    n.name.toLowerCase().includes(searchReportQuery.value.toLocaleLowerCase()),
  ),
)

watch(
  () => mapStore.selectedNeighborhood,
  (newVal) => {
    if (newVal) putManualLocation.value = ''
  },
)

const displayNeighborhood = computed(() => {
  if (mapStore.isSearching) return 'Buscando...'
  return (
    putManualLocation.value ||
    mapStore.selectedNeighborhood ||
    mapStore.detectLocation ||
    'Detectando...'
  )
})

const selectManual = (name: string) => {
  putManualLocation.value = name
  isChangingReport.value = false
  mapStore.setSelectedNeighborhood('')
}

const handleReport = async () => {
  console.log(`Enviado para a API o reporte: ${displayNeighborhood.value}`)
  const reportedNeighborhood = displayNeighborhood.value

  if (
    !reportedNeighborhood ||
    reportedNeighborhood === 'Detectando...' ||
    reportedNeighborhood === 'Fora de area.'
  )
    return

  try {
    const token = localStorage.getItem('userToken')
    const neighborhoodSearchId = mapStore.neighborhoodsList.find(
      (n) => n.name === reportedNeighborhood,
    )

    if (!neighborhoodSearchId) {
      console.error('Não foi encontrado o bairro na lista.')
      return
    }

    powerStore.doReport(reportedNeighborhood)

    console.log(`Reportado o bairro: ${reportedNeighborhood}`)

    emit('reportAdded', reportedNeighborhood)

    putManualLocation.value = ''
    mapStore.setSelectedNeighborhood('')
  } catch (e) {
    console.error('Falha ao processar reporte: ', e)
    throw e
  }
}

const cancelChange = () => {
  isChangingReport.value = false
  putManualLocation.value = ''
}
</script>

<template>
  <div class="box-report-wrapper">
    <div class="box-report-card">
      <template v-if="!isChangingReport">
        <p class="box-report-label">Reportar falta de luz em:</p>
        <h3 class="box-report-neighborhood">{{ displayNeighborhood }}</h3>
        <button
          class="box-report-btn-main"
          :disabled="
            ['Fora de area.', 'Detectando...', 'Buscando...'].includes(displayNeighborhood)
          "
          @click="handleReport"
        >
          LOCAL SEM LUZ
        </button>
        <button class="box-report-btn-change" @click="isChangingReport = true">Mudar bairro</button>
      </template>
      <template v-else>
        <input
          v-model="searchReportQuery"
          type="text"
          placeholder="Buscar bairro..."
          class="box-report-input"
          autofocus
        />
        <ul class="box-report-dropdown">
          <li v-for="n in filteredNeighborhoods" :key="n.id" @click="selectManual(n.name)">
            {{ n.name }}
          </li>
        </ul>
        <button class="box-report-btn-change" @click="cancelChange">Cancelar</button>
      </template>
    </div>
  </div>
</template>
