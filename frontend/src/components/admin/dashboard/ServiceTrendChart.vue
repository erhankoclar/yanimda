<script setup>
import Chart from 'primevue/chart'
import SelectButton from 'primevue/selectbutton'
import Skeleton from 'primevue/skeleton'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { seriesTotal, toLineChartData } from '@/admin/chartData'
import { formatShortDate } from '@/admin/format'
import { usePreferencesStore } from '@/stores/preferences'

const props = defineProps({
  /** Dashboard yanıtındaki `series`; ilk yüklemede null. */
  series: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

/** Grafik aralığı (gün) ve kaynak seçimi; üst bileşen yeniden yükler. */
const days = defineModel('days', { type: Number, default: 30 })
const source = defineModel('source', { type: String, default: 'all' })

const { t } = useI18n()
const preferences = usePreferencesStore()
const root = ref(null)

const rangeOptions = computed(() => [7, 30, 90].map((value) => ({ value, label: t('admin.dashboard.trend.days', { count: value }) })))
const sourceOptions = computed(() => ['all', 'inquiries', 'requests'].map((value) => ({ value, label: t(`admin.dashboard.trend.sources.${value}`) })))

const chartData = computed(() => (props.series ? toLineChartData(props.series) : null))
const isEmpty = computed(() => props.series !== null && seriesTotal(props.series) === 0)
const isWeekly = computed(() => props.series?.bucket === 'week')

// Eksen ve lejant renkleri admin token'larından okunur; tema değişince yeniden hesaplanır.
const palette = ref({ ink: '#5b6662', line: '#e2e7e5' })

/** Etkin temanın eksen renklerini CSS değişkenlerinden okur. */
function readPalette() {
  if (!root.value) return
  const style = getComputedStyle(root.value)
  palette.value = {
    ink: style.getPropertyValue('--admin-ink-soft').trim() || palette.value.ink,
    line: style.getPropertyValue('--admin-line').trim() || palette.value.line,
  }
}

onMounted(readPalette)
watch(() => preferences.theme, () => nextTick(readPalette))

// Hareket azaltma tercihinde grafik animasyonsuz çizilir.
const reducedMotion = typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

const chartOptions = computed(() => ({
  maintainAspectRatio: false,
  animation: reducedMotion ? false : { duration: 400 },
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'bottom', labels: { color: palette.value.ink, usePointStyle: true, boxWidth: 8, padding: 16 } },
    tooltip: {
      callbacks: {
        // Haftalık görünümde ipucu başlığı haftanın başlangıcını açıkça söyler.
        title: (items) => (isWeekly.value ? t('admin.dashboard.trend.weekOf', { date: items[0].label }) : items[0].label),
      },
    },
  },
  scales: {
    x: { ticks: { color: palette.value.ink, maxRotation: 0, autoSkipPadding: 12 }, grid: { display: false } },
    y: { beginAtZero: true, ticks: { color: palette.value.ink, precision: 0 }, grid: { color: palette.value.line } },
  },
}))
</script>

<template>
  <section ref="root" class="admin-panel trend" aria-labelledby="trend-title">
    <div class="admin-panel__head">
      <h2 id="trend-title">{{ t('admin.dashboard.trend.title') }}</h2>
      <div class="trend__filters">
        <span id="trend-source-label" class="visually-hidden">{{ t('admin.dashboard.trend.sourceLabel') }}</span>
        <SelectButton
          v-model="source"
          class="trend__source"
          :options="sourceOptions"
          optionLabel="label"
          optionValue="value"
          :allowEmpty="false"
          size="small"
          ariaLabelledby="trend-source-label"
        />
        <span id="trend-range-label" class="visually-hidden">{{ t('admin.dashboard.trend.rangeLabel') }}</span>
        <SelectButton
          v-model="days"
          class="trend__range"
          :options="rangeOptions"
          optionLabel="label"
          optionValue="value"
          :allowEmpty="false"
          size="small"
          ariaLabelledby="trend-range-label"
        />
      </div>
    </div>

    <div class="trend__body" :aria-busy="loading ? 'true' : 'false'">
      <Skeleton v-if="!series" height="100%" />
      <p v-else-if="isEmpty" class="trend__empty">{{ t('admin.dashboard.trend.empty') }}</p>
      <Chart v-else type="line" :data="chartData" :options="chartOptions" class="trend__chart" aria-hidden="true" />
    </div>

    <!-- Grafiği göremeyenler için aynı veri tablo olarak verilir; tablo genişliği taşmasın diye kapsayıcı gizlenir. -->
    <div v-if="series && !isEmpty" class="visually-hidden">
      <table>
        <caption>{{ t('admin.dashboard.trend.tableCaption') }}</caption>
        <thead>
          <tr>
            <th scope="col">{{ isWeekly ? t('admin.dashboard.trend.weekColumn') : t('admin.dashboard.trend.dateColumn') }}</th>
            <th v-for="dataset in series.datasets" :key="dataset.service_id" scope="col">{{ dataset.name }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(label, index) in series.labels" :key="label">
            <th scope="row">{{ formatShortDate(label) }}</th>
            <td v-for="dataset in series.datasets" :key="dataset.service_id">{{ dataset.counts[index] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.trend {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.trend__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.trend__body {
  position: relative;
  /* Grafik genişliğini kapsayıcı belirler; canvas kapsayıcıyı büyütüp yeniden boyutlanma döngüsü kurmasın. */
  overflow: hidden;
  flex: 1;
  height: 18rem;
  min-height: 18rem;
}

.trend__chart {
  position: relative;
  width: 100%;
  height: 100%;
}

.trend__empty {
  display: grid;
  height: 100%;
  margin: 0;
  place-items: center;
  color: var(--admin-ink-soft);
}

@media (min-width: 48rem) {
  .trend__body {
    height: 20rem;
  }
}
</style>
