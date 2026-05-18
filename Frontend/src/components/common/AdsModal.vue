<script setup lang="ts">
const props = defineProps<{
  show: boolean
  latestReportedNeighborhood: string
}>()
const emit = defineEmits<{
  close: []
}>()
const closeAds = () => {
  emit('close')
}
</script>

<template>
  <Transition name="pop">
    <div v-if="show" class="box-ads-tab" @click.self="closeAds">
      <div class="box-ads-card">
        <div class="ads-header">
          <span class="ads-tag">Patrocinios</span>
          <button class="ads-close" @click="closeAds">X</button>
        </div>
        <div class="ads-body">
          <h2>BAIRRO REPORTADO!</h2>
          <p>
            O bairro <strong>{{ latestReportedNeighborhood }}</strong> acaba de ser reportado.
          </p>
          <div class="ads-ad-grid">
            <div v-for="n in 8" :key="n" class="ads-ad-slot">
              <div class="ads-placeholder">
                <img src="../../assets/images/advertise.svg" class="ads-icon-mini" />
                <span>Ad {{ n }}</span>
              </div>
            </div>
          </div>
        </div>
        <button class="ads-confirm-btn" @click="closeAds">ENTENDIDO</button>
      </div>
    </div>
  </Transition>
</template>
