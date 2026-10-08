<script setup>
import Button from 'primevue/button'
import Message from 'primevue/message'
import Select from 'primevue/select'
import SelectButton from 'primevue/selectbutton'
import Skeleton from 'primevue/skeleton'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { formatNumber } from '@/admin/format'
import { countFor } from '@/admin/map/thematic'
import { useMapData } from '@/admin/map/useMapData'
import AreaRanking from '@/components/admin/map/AreaRanking.vue'
import AreaRecordsDrawer from '@/components/admin/map/AreaRecordsDrawer.vue'
import MapLegend from '@/components/admin/map/MapLegend.vue'
import ThematicMap from '@/components/admin/map/ThematicMap.vue'
import { usePreferencesStore } from '@/stores/preferences'

const { t } = useI18n()
const preferences = usePreferencesStore()
const { source, days, boundaries, data, loading, error, load } = useMapData()

// 0: tüm hizmetler (PrimeVue Select null değeri "seçim yok" saydığı için 0 kullanılır).
const serviceValue = ref(0)
const serviceId = computed(() => serviceValue.value || null)
// Haritada görünen seviye; sıralama paneli varsayılan olarak bunu izler.
const mapLevel = ref('city')
const rankingLevel = ref('district')
const selectedArea = ref(null)
const drawerOpen = ref(false)

const sourceOptions = computed(() => ['all', 'inquiries', 'requests'].map((value) => ({ value, label: t(`admin.dashboard.trend.sources.${value}`) })))
const periodOptions = computed(() => [30, 90, 365, null].map((value) => ({
  value,
  label: value ? t(`admin.map.periods.${value}`) : t('admin.map.periods.all'),
})))
const serviceOptions = computed(() => [
  { value: 0, label: t('admin.map.allServices') },
  ...(data.value?.services ?? []).map((service) => ({ value: service.id, label: `${service.name} (${formatNumber(service.count)})` })),
])

const selectedService = computed(() => data.value?.services.find((service) => service.id === serviceId.value) ?? null)
// Toplamın başlığı: hizmet seçiliyse hizmet adı, değilse il geneli.
const totalLabel = computed(() => selectedService.value?.name ?? t('admin.map.city'))

const total = computed(() => {
  if (!data.value) return 0
  return serviceId.value ? selectedService.value?.count ?? 0 : data.value.total
})

// Lejant, haritada o an görünen seviyenin sayılarını kullanır.
const legendValues = computed(() => {
  if (!data.value) return []
  if (mapLevel.value === 'city') return [total.value]
  const items = mapLevel.value === 'neighborhood' ? data.value.neighborhoods : data.value.districts
  return items.map((item) => countFor(item, serviceId.value))
})

/**
 * Harita seviyesi değişince sıralama paneli de o seviyeye geçer (il seviyesinde ilçeler listelenir).
 *
 * @param {'city' | 'district' | 'neighborhood'} level Yeni seviye.
 */
function onLevel(level) {
  mapLevel.value = level
  rankingLevel.value = level === 'neighborhood' ? 'neighborhood' : 'district'
}

/**
 * Bir alanın kayıt listesini çekmecede açar.
 *
 * @param {{ level: string, id: number | null, name: string, count: number }} area Seçilen alan.
 */
function openArea(area) {
  selectedArea.value = area
  drawerOpen.value = true
}
</script>

<template>
  <div class="map-page">
    <section class="admin-panel map-page__toolbar" :aria-label="t('admin.map.filters')">
      <div class="map-page__total">
        <span class="map-page__total-label">{{ totalLabel }}</span>
        <strong>{{ formatNumber(total) }}</strong>
        <span class="map-page__total-label">{{ t('admin.map.totalLabel') }}</span>
      </div>
      <div class="map-page__filters">
        <label id="map-service-label" class="visually-hidden" for="map-service">{{ t('admin.map.service') }}</label>
        <Select
          v-model="serviceValue"
          inputId="map-service"
          ariaLabelledby="map-service-label"
          :options="serviceOptions"
          optionLabel="label"
          optionValue="value"
          size="small"
          class="map-page__service"
        />
        <SelectButton
          v-model="source"
          :options="sourceOptions"
          optionLabel="label"
          optionValue="value"
          :allowEmpty="false"
          size="small"
          :ariaLabel="t('admin.dashboard.trend.sourceLabel')"
        />
        <SelectButton
          v-model="days"
          :options="periodOptions"
          optionLabel="label"
          optionValue="value"
          :allowEmpty="false"
          size="small"
          :ariaLabel="t('admin.map.period')"
        />
      </div>
    </section>

    <Message v-if="error" severity="error" :closable="false" role="alert" class="map-page__error">
      <span>{{ error }}</span>
      <Button :label="t('admin.dashboard.retry')" size="small" text @click="load" />
    </Message>

    <div class="map-page__body">
      <section class="admin-panel map-page__map" :aria-busy="loading ? 'true' : 'false'">
        <Skeleton v-if="!boundaries || !data" height="100%" />
        <template v-else>
          <ThematicMap
            :boundaries="boundaries"
            :districts="data.districts"
            :neighborhoods="data.neighborhoods"
            :total="total"
            :service-id="serviceId"
            :theme="preferences.theme"
            @level="onLevel"
            @select="openArea"
          />
          <MapLegend class="map-page__legend" :values="legendValues" :theme="preferences.theme" />
          <p class="map-page__hint">{{ t('admin.map.zoomHint') }}</p>
        </template>
      </section>

      <AreaRanking
        v-if="data"
        v-model:level="rankingLevel"
        class="map-page__ranking"
        :districts="data.districts"
        :neighborhoods="data.neighborhoods"
        :service-id="serviceId"
        @select="openArea"
      />
    </div>

    <p class="map-page__note">{{ t('admin.map.note') }}</p>

    <AreaRecordsDrawer
      v-model:visible="drawerOpen"
      :area="selectedArea"
      :source="source"
      :service-id="serviceId"
      :days="days"
    />
  </div>
</template>

<style scoped>
.map-page {
  display: grid;
  gap: 1.25rem;
}

.map-page__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.map-page__total {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.map-page__total strong {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif;
  font-size: 1.9rem;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.map-page__total-label {
  color: var(--admin-ink-soft);
  font-weight: 700;
}

.map-page__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.map-page__service {
  min-width: 14rem;
}

.map-page__error :deep(.p-message-text) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.map-page__body {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1.25rem;
}

.map-page__map {
  position: relative;
  height: 30rem;
  padding: 0;
  overflow: hidden;
}

.map-page__legend {
  position: absolute;
  bottom: 3.25rem;
  left: 0.75rem;
}

@media (min-width: 48rem) {
  .map-page__legend {
    bottom: 2rem;
  }
}

.map-page__hint {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  max-width: calc(100% - 4rem);
  margin: 0;
  padding: 0.3rem 0.6rem;
  border-radius: 0.5rem;
  background: color-mix(in srgb, var(--admin-surface) 90%, transparent);
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
  pointer-events: none;
}

.map-page__ranking {
  min-height: 0;
}

.map-page__note {
  margin: 0;
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
}

@media (min-width: 75rem) {
  .map-page__body {
    grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
  }

  .map-page__map,
  .map-page__ranking {
    height: 38rem;
    max-height: none;
  }
}
</style>
