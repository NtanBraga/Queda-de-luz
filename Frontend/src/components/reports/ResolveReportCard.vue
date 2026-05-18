<script setup lang="ts">
import { powerOutageStore } from '@/stores/powerOutage'
import { authAccountStore } from '@/stores/auth'
import { mapBuildStore } from '@/stores/map'
import { resolveReport } from '@/scripts/user/reports'
import { storeToRefs } from 'pinia'

const powerStore = powerOutageStore()
const authStore = authAccountStore()
const mapStore = mapBuildStore()

const { resolveNeighborhoodName } = storeToRefs(powerStore)

const handleResolve = async () => {
  try {
    const districtName = resolveNeighborhoodName.value
    if (!districtName) return

    const getToken = localStorage.getItem('userToken')!

    const districtId = mapStore.neighborhoodsList.find((n) => n.name === districtName)!

    
    await resolveReport(districtId.id, getToken)

    powerStore.fixIndexResolve(districtName)

    console.log(`Bairro voltou com a luz: ${districtName}`)
  } catch (e) {
    console.error('Erro ao resolver reporte:', e)
  }
}

const handleNext = () => {
  powerStore.nextResolve()
}
</script>

<template>
  <Transition name="pop">
    <div
      v-if="authStore.isLoggedIn && powerStore.stillNoPower.length > 0"
      class="box-report-resolvecard"
    >
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
          <button class="box-report-resolvecard-btc-no">CONTINUA SEM LUZ</button>
        </div>
      </div>
    </div>
  </Transition>
</template>
