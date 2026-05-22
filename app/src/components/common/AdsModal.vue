<script setup lang="ts">
import { nextTick, watch, ref } from 'vue'

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

const confirmBtn = ref<HTMLButtonElement | null>(null)

watch(
  () => props.show,
  async (isShowing) => {
    if (isShowing) {
      await nextTick()
      confirmBtn.value?.focus()
    }
  },
)
</script>

<template>
  <Transition name="pop">
    <div v-if="show" class="box-ads-tab" @click.self="closeAds" @keydown.escape="closeAds">
      <div class="box-ads-card" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="ads-header">
          <span class="ads-tag">Patrocinios</span>
          <button class="ads-close" @click="closeAds" aria-label="Fechar modal">X</button>
        </div>
        <div class="ads-body">
          <h2>BAIRRO REPORTADO!</h2>
          <p>
            O bairro <strong>{{ latestReportedNeighborhood }}</strong> acaba de ser reportado.
          </p>
          <div class="ads-ad-grid">
            <div
              v-for="n in 8"
              :key="n"
              class="ads-ad-slot"
              tabindex="0"
              :aria-label="`Anúncio parceiro ${n}`"
            >
              <div class="ads-placeholder">
                <img
                  src="../../assets/images/advertise.svg"
                  class="ads-icon-mini"
                  alt="Imagem de patrocinio"
                />
                <span>Ad {{ n }}</span>
              </div>
            </div>
          </div>
        </div>
        <button ref="confirmBtn" class="ads-confirm-btn" @click="closeAds">ENTENDIDO</button>
      </div>
    </div>
  </Transition>
</template>
