<script setup lang="ts">
import { mapBuildStore } from '@/stores/map'
import { powerOutageStore } from '@/stores/powerOutage'
import { computed } from 'vue'

const powerStore = powerOutageStore()
const mapStore = mapBuildStore()

interface NewItem {
  text: string
  type: 'manutencao-agora' | 'falta-de-luz' | 'desligamento-futuro' | 'estavel'
}

const newList = computed(() => {
  const news: NewItem[] = []

  if (powerStore.scheduledOutages && powerStore.scheduledOutages.length > 0) {
    powerStore.scheduledOutages.forEach((neighborhood) => {
      news.push({
        text: `Manutenção ocorrendo no bairro ${neighborhood}`,
        type: 'manutencao-agora',
      })
    })
  }

  if (powerStore.neighborhoodsNoPower && powerStore.neighborhoodsNoPower.length > 0) {
    powerStore.neighborhoodsNoPower.forEach((neighborhood) => {
      const reports = powerStore.reportCount[neighborhood] || 0
      news.push({
        text: `Falta de luz reportada em ${neighborhood} (${reports} ${reports > 1 ? 'reportes' : 'reporte'})`,
        type: 'falta-de-luz',
      })
    })
  }

  if (powerStore.upcomingOutagesList && powerStore.upcomingOutagesList.length > 0) {
    const now = new Date()

    powerStore.upcomingOutagesList.forEach((outage) => {
      const [day, month, year] = outage.data.split('/')
      const [hour, minute] = outage.horario_inicio.split(':')
      const dataStartEvent = new Date(
        Number(year),
        Number(month) - 1,
        Number(day),
        Number(hour),
        Number(minute),
      )

      if (dataStartEvent > now) {
        news.push({
          text: `Desligamentos programados: Partes do bairro ${outage.bairro} ficará sem luz dia ${outage.data} das ${outage.horario_inicio} às ${outage.horario_fim}`,
          type: 'desligamento-futuro',
        })
      }
    })
  }

  if (news.length === 0) {
    news.push({
      text: `${mapStore.city} está completamente estável no momento!!`,
      type: 'estavel',
    })
  }

  return news
})

const currentNews = computed(() => {
  return newList.value.join('  •  ')
})

const newsSpeed = computed(() => {
  const calculatedTime = Math.max(15, newList.value.length * 4)
  return `${calculatedTime}s`
})
</script>
<template>
  <div class="box-news">
    <div class="news-content">
      <p class="news-text" :style="{ animationDuration: newsSpeed }">
        <span v-for="(news, index) in newList" :key="index">
          <span :class="news.type">{{ news.text }}</span>
          <span v-if="index < newList.length - 1" class="news-separator"
            >&nbsp;&nbsp;&bull;&nbsp;&nbsp;</span
          >
        </span>
      </p>
    </div>
  </div>
</template>
