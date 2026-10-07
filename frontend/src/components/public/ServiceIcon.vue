<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** Backend'deki hizmetin `icon` anahtarı. */
  name: { type: String, required: true },
})

// Her ikon 48x48 görünüm alanında, kalın uçlu çizgilerle çizilir.
const ICONS = {
  'home-care': ['M8 22 24 9l16 13', 'M12 19v20h24V19', 'M24 35s-7-4.3-7-9a4 4 0 0 1 7-2.6 4 4 0 0 1 7 2.6c0 4.7-7 9-7 9Z'],
  companion: ['M17 21a6 6 0 1 0 0-12 6 6 0 0 0 0 12Z', 'M31 21a6 6 0 1 0 0-12 6 6 0 0 0 0 12Z', 'M6 39c0-7 5-12 11-12s11 5 11 12', 'M26 29c1.5-1.3 3.2-2 5-2 6 0 11 5 11 12'],
  hospital: ['M10 8h28v32H10z', 'M24 15v14', 'M17 22h14', 'M20 40v-6h8v6'],
  shopping: ['M10 16h28l-3 24H13L10 16Z', 'M18 20v-6a6 6 0 0 1 12 0v6'],
  health: ['M24 40S7 30 7 18a8.5 8.5 0 0 1 17-3 8.5 8.5 0 0 1 17 3c0 12-17 22-17 22Z', 'M12 24h6l3-5 4 10 3-5h8'],
  repair: ['M29 9a8 8 0 0 0-9 11L9 31a3.5 3.5 0 0 0 5 5l11-11a8 8 0 0 0 11-9l-5 5-5-1-1-5 5-5Z'],
}

// Bilinmeyen anahtarlar için yuvarlak bir yer tutucu çizilir.
const paths = computed(() => ICONS[props.name] ?? ['M24 40a16 16 0 1 0 0-32 16 16 0 0 0 0 32Z'])
</script>

<template>
  <svg class="service-icon" viewBox="0 0 48 48" aria-hidden="true" focusable="false">
    <path v-for="(path, index) in paths" :key="index" :d="path" />
  </svg>
</template>

<style scoped>
.service-icon {
  width: 3rem;
  height: 3rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
