<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { formatNumber } from '@/admin/format'
import { classBreaks, colorRamp, legendRows } from '@/admin/map/thematic'

const props = defineProps({
  /** Görünen seviyedeki alanların sayıları. */
  values: { type: Array, required: true },
  theme: { type: String, default: 'light' },
})

const { t } = useI18n()

const max = computed(() => Math.max(0, ...props.values))
const rows = computed(() => legendRows(classBreaks(props.values), max.value, colorRamp(props.theme)))

/**
 * Bir lejant satırının aralık metnini üretir.
 *
 * @param {{ from: number, to: number }} row Satır.
 * @returns {string} "3" veya "3–7" biçiminde metin.
 */
function rangeText(row) {
  return row.from === row.to ? formatNumber(row.from) : `${formatNumber(row.from)}–${formatNumber(row.to)}`
}
</script>

<template>
  <div class="map-legend">
    <p class="map-legend__title">{{ t('admin.map.legend') }}</p>
    <p v-if="!rows.length" class="map-legend__empty">{{ t('admin.map.legendEmpty') }}</p>
    <ul v-else>
      <li v-for="row in rows" :key="row.from">
        <span class="map-legend__swatch" :style="{ background: row.color }" aria-hidden="true" />
        {{ rangeText(row) }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.map-legend {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--admin-line);
  border-radius: 0.6rem;
  background: color-mix(in srgb, var(--admin-surface) 92%, transparent);
  box-shadow: var(--admin-shadow);
  font-size: 0.8rem;
}

.map-legend__title {
  margin: 0 0 0.35rem;
  font-weight: 700;
}

.map-legend ul {
  display: grid;
  gap: 0.2rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.map-legend li {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-variant-numeric: tabular-nums;
}

.map-legend__swatch {
  width: 1.1rem;
  height: 0.75rem;
  border-radius: 0.2rem;
}

.map-legend__empty {
  margin: 0;
  color: var(--admin-ink-soft);
}
</style>
