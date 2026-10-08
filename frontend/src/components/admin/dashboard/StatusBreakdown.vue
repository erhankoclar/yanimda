<script setup>
import Chart from 'primevue/chart'
import Skeleton from 'primevue/skeleton'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { formatNumber } from '@/admin/format'
import { statusColor } from '@/admin/status'
import { statusLabel } from '@/constants/care'
import { usePreferencesStore } from '@/stores/preferences'

const props = defineProps({
  /** Dashboard yanıtındaki `status_breakdown`; ilk yüklemede null. */
  items: { type: Array, default: null },
})

const { t } = useI18n()
const preferences = usePreferencesStore()
const root = ref(null)

const total = computed(() => (props.items ?? []).reduce((sum, item) => sum + item.count, 0))

// Halka dilimlerinin arasındaki boşluk kart zemini renginde olsun; tema değişince yeniden okunur.
const surface = ref('#ffffff')

/** Kart zemin rengini CSS değişkeninden okur. */
function readSurface() {
  if (!root.value) return
  surface.value = getComputedStyle(root.value).getPropertyValue('--admin-surface').trim() || surface.value
}

onMounted(readSurface)
watch(() => preferences.theme, () => nextTick(readSurface))

const chartData = computed(() => ({
  labels: props.items.map((item) => statusLabel(item.status)),
  datasets: [{
    data: props.items.map((item) => item.count),
    backgroundColor: props.items.map((item) => statusColor(item.status)),
    borderColor: surface.value,
    borderWidth: 2,
  }],
}))

const reducedMotion = typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

// Lejant grafiğin altında, sayılarla birlikte HTML olarak verilir; Chart.js lejantı kapalıdır.
const chartOptions = {
  cutout: '68%',
  maintainAspectRatio: false,
  animation: reducedMotion ? false : { duration: 400 },
  plugins: { legend: { display: false } },
}
</script>

<template>
  <section ref="root" class="admin-panel breakdown" aria-labelledby="breakdown-title">
    <div class="admin-panel__head">
      <h2 id="breakdown-title">{{ t('admin.dashboard.status.title') }}</h2>
    </div>

    <Skeleton v-if="!items" shape="circle" size="10rem" class="breakdown__skeleton" />
    <p v-else-if="!total" class="breakdown__empty">{{ t('admin.dashboard.status.empty') }}</p>
    <template v-else>
      <div class="breakdown__chart">
        <Chart type="doughnut" :data="chartData" :options="chartOptions" class="breakdown__canvas" aria-hidden="true" />
        <div class="breakdown__total" aria-hidden="true">
          <strong>{{ formatNumber(total) }}</strong>
          <span>{{ t('admin.dashboard.status.total') }}</span>
        </div>
      </div>
      <ul class="breakdown__legend">
        <li v-for="item in items" :key="item.status" :data-status="item.status">
          <span class="breakdown__swatch" :style="{ background: statusColor(item.status) }" aria-hidden="true" />
          <span class="breakdown__label">{{ statusLabel(item.status) }}</span>
          <span class="breakdown__count">{{ formatNumber(item.count) }}</span>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.breakdown {
  min-width: 0;
}

.breakdown__chart {
  position: relative;
  height: 11rem;
}

/* Chart.js oranı korumadığında boyutu kapsayıcıdan alır; kök öğe kapsayıcıyı tam doldurmalıdır. */
.breakdown__canvas {
  position: relative;
  width: 100%;
  height: 100%;
}

/* Toplam halkanın ortasında; grafik etkileşimini engellemez. */
.breakdown__total {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  text-align: center;
  pointer-events: none;
}

.breakdown__total strong {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif;
  font-size: 1.6rem;
  line-height: 1.1;
}

.breakdown__total span {
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
}

.breakdown__legend {
  display: grid;
  gap: 0.35rem;
  margin: 1rem 0 0;
  padding: 0;
  list-style: none;
}

.breakdown__legend li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.5rem;
}

.breakdown__swatch {
  width: 0.7rem;
  height: 0.7rem;
  border-radius: 50%;
}

.breakdown__count {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.breakdown__skeleton {
  margin: 0 auto;
}

.breakdown__empty {
  margin: 0;
  color: var(--admin-ink-soft);
}
</style>
