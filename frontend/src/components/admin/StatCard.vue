<script setup>
import Skeleton from 'primevue/skeleton'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { changeInfo, formatNumber } from '@/admin/format'

const props = defineProps({
  /** PrimeIcons sınıfı (ör. `pi pi-inbox`); başlıkta ve filigranda kullanılır. */
  icon: { type: String, required: true },
  title: { type: String, required: true },
  /** Gösterilecek sayı; yüklenirken null. */
  value: { type: Number, default: null },
  /**
   * Geçen aya göre değişim yüzdesi. `undefined`: kart kıyas göstermez;
   * `null`: önceki dönemde veri yoktu.
   */
  change: { type: Number, default: undefined },
  /** Kıyas yoksa alt satırda gösterilecek kısa bilgi. */
  note: { type: String, default: '' },
  /** İkon çipinin rengi. */
  tone: { type: String, default: 'primary', validator: (value) => ['primary', 'accent'].includes(value) },
  loading: { type: Boolean, default: false },
})

const { t } = useI18n()

const hasComparison = computed(() => props.change !== undefined)
const comparison = computed(() => changeInfo(props.change))
const formattedValue = computed(() => formatNumber(props.value))

// Ekran okuyucu için yön sözcükle de verilir; ok işareti yalnızca görseldir.
const trendLabel = computed(() => ({
  up: t('admin.dashboard.compare.increase'),
  down: t('admin.dashboard.compare.decrease'),
}[comparison.value.trend] ?? ''))
</script>

<template>
  <article class="stat-card" :class="`stat-card--${tone}`">
    <i :class="['stat-card__watermark', icon]" aria-hidden="true" />

    <header class="stat-card__head">
      <span class="stat-card__chip"><i :class="icon" aria-hidden="true" /></span>
      <h2 class="stat-card__title">{{ title }}</h2>
    </header>

    <div class="stat-card__value">
      <Skeleton v-if="loading || value === null" width="5rem" height="2.4rem" />
      <template v-else>{{ formattedValue }}</template>
    </div>

    <div class="stat-card__foot">
      <Skeleton v-if="loading" width="70%" height="1rem" />
      <template v-else-if="hasComparison && comparison.trend === 'none'">
        {{ t('admin.dashboard.compare.noPrevious') }}
      </template>
      <template v-else-if="hasComparison && comparison.trend === 'flat'">
        {{ t('admin.dashboard.compare.unchanged') }}
      </template>
      <template v-else-if="hasComparison">
        <span class="stat-card__trend" :class="`stat-card__trend--${comparison.trend}`">
          <span aria-hidden="true">{{ comparison.trend === 'up' ? '▲' : '▼' }}</span>
          <span class="visually-hidden">{{ trendLabel }}</span>
          {{ comparison.text }}
        </span>
        {{ t('admin.dashboard.compare.vsLastMonth') }}
      </template>
      <template v-else>{{ note }}</template>
    </div>
  </article>
</template>

<style scoped>
.stat-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  min-height: 9.5rem;
  padding: 1.15rem 1.25rem;
  overflow: hidden;
  border: 1px solid var(--admin-line);
  border-radius: var(--admin-radius);
  background: var(--admin-surface);
  box-shadow: var(--admin-shadow);
}

/* Sağdaki büyük, soluk ikon; içerikle çakışmasın diye tıklanamaz ve arkada durur. */
.stat-card__watermark {
  position: absolute;
  top: 50%;
  right: -0.75rem;
  font-size: 6.5rem;
  opacity: 0.07;
  pointer-events: none;
  transform: translateY(-50%);
}

.stat-card--primary .stat-card__watermark {
  color: var(--admin-primary);
}

.stat-card--accent .stat-card__watermark {
  color: var(--admin-accent);
}

.stat-card__head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  /* Başlık iki satıra kaysa da yan kartlardaki sayılar aynı hizada kalır. */
  min-height: 2.75rem;
}

.stat-card__chip {
  display: inline-grid;
  flex: none;
  place-items: center;
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 0.6rem;
}

.stat-card--primary .stat-card__chip {
  background: var(--admin-primary-tint);
  color: var(--admin-primary);
}

.stat-card--accent .stat-card__chip {
  background: color-mix(in srgb, var(--admin-accent) 18%, transparent);
  color: var(--admin-accent-ink);
}

.stat-card__title {
  color: var(--admin-ink-soft);
  font-family: inherit;
  font-size: 0.92rem;
  font-weight: 700;
  letter-spacing: 0;
}

.stat-card__value {
  position: relative;
  margin: 0;
  font-family: 'Bricolage Grotesque', system-ui, sans-serif;
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.stat-card__foot {
  position: relative;
  /* Kartlar eşit yükseklikte; alt satır en alta yaslanır, başlıklar aynı hizada kalır. */
  margin: auto 0 0;
  color: var(--admin-ink-soft);
  font-size: 0.85rem;
}

.stat-card__trend {
  font-weight: 700;
}

.stat-card__trend--up {
  color: var(--admin-success);
}

.stat-card__trend--down {
  color: var(--admin-danger);
}
</style>
