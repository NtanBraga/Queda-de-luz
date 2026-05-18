<script setup lang="ts">
import { powerOutageStore } from '@/stores/powerOutage'
import { storeToRefs } from 'pinia'
import { ref, watch } from 'vue'

const powerStore = powerOutageStore()

const { resolveNeighborhoodName } = storeToRefs(powerStore)

const isDismissed = ref(false)

const handleResolve = async () => {
  try {
    const districtName = resolveNeighborhoodName.value
    if (!districtName) return

    powerStore.fixIndexResolve(districtName)

    console.log(`Bairro voltou com a luz: ${districtName}`)
  } catch (e) {
    console.error('Erro ao resolver reporte:', e)
  }
}

const handleStillNoPower = () => {
  isDismissed.value = true
}

const handleNext = () => {
  powerStore.nextResolve()
}

watch(
  () => powerStore.stillNoPower.length,
  (newLength) => {
    if (newLength > 0) {
      isDismissed.value = false
    }
  },
)
</script>

<template>
  <Transition name="pop">
    <div v-if="powerStore.stillNoPower.length > 0 && !isDismissed" class="box-report-resolvecard">
      <div class="box-report-resolvecard-question">
        <h2>
          A luz no bairro <strong>{{ powerStore.resolveNeighborhoodName }}</strong> voltou?
        </h2>
        <div class="box-report-resolvecard-actions">
          <button class="box-report-resolvecard-btc-yes" @click="handleResolve">
            SIM, VOLTOU!
          </button>
          <button
            v-if="powerStore.stillNoPower.length > 1"
            class="box-report-resolve-card-next"
            @click="handleNext"
          >
            VER OUTRO BAIRRO ({{ powerStore.currentResolveIndex + 1 }}/{{
              powerStore.stillNoPower.length
            }})
          </button>
          <button class="box-report-resolvecard-btc-no" @click="handleStillNoPower">
            CONTINUA SEM LUZ
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>
