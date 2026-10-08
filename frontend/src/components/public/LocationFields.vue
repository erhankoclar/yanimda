<script setup>
import { computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseSelect from './BaseSelect.vue'

import { useLocations } from '@/composables/useLocations'

/** Seçili ilçe ve mahalle kimlikleri; ilçe değişince mahalle sıfırlanır. */
const district = defineModel('district', { type: [Number, String], default: '' })
const neighborhood = defineModel('neighborhood', { type: [Number, String], default: '' })

defineProps({
  /** Alan hataları: `district` ve `neighborhood`. */
  errors: { type: Object, default: () => ({}) },
})

const { t } = useI18n()
const { districts, neighborhoodsByDistrict, loadDistricts, loadNeighborhoods } = useLocations()

const districtOptions = computed(() => districts.value.map((item) => ({ value: item.id, label: item.name })))
const neighborhoodOptions = computed(() => (neighborhoodsByDistrict.value[Number(district.value)] ?? [])
  .map((item) => ({ value: item.id, label: item.name })))

onMounted(() => {
  loadDistricts().catch(() => {})
  if (district.value) loadNeighborhoods(Number(district.value)).catch(() => {})
})

watch(district, (value, previous) => {
  if (previous !== undefined && value !== previous) neighborhood.value = ''
  if (value) loadNeighborhoods(Number(value)).catch(() => {})
})
</script>

<template>
  <div class="location-fields">
    <BaseSelect
      v-model="district"
      :label="t('location.district')"
      :options="districtOptions"
      required
      :error="errors.district"
    />
    <BaseSelect
      v-model="neighborhood"
      :label="t('location.neighborhood')"
      :options="neighborhoodOptions"
      :placeholder="district ? '' : t('location.chooseDistrictFirst')"
      :disabled="!district"
      required
      :error="errors.neighborhood"
    />
  </div>
</template>

<style scoped>
.location-fields {
  display: grid;
  gap: 0 var(--space-4);
}

@media (min-width: 36rem) {
  .location-fields {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
