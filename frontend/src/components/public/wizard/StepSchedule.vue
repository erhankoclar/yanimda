<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseInput from '../BaseInput.vue'
import BaseSelect from '../BaseSelect.vue'
import BaseTextarea from '../BaseTextarea.vue'

import { MAX_PREFERRED_DAYS_AHEAD, TIME_SLOT_OPTIONS, localizedOptions } from '@/constants/care'
import { isoDateAfter, toIsoDate } from '@/utils/dates'

defineProps({
  form: { type: Object, required: true },
  errors: { type: Object, required: true },
})

const { t } = useI18n()

// Zaman aralığı seçenekleri etkin dilde.
const timeSlotOptions = computed(() => localizedOptions(TIME_SLOT_OPTIONS))

const minDate = toIsoDate(new Date())
const maxDate = isoDateAfter(MAX_PREFERRED_DAYS_AHEAD)
</script>

<template>
  <div>
    <BaseInput
      v-model="form.preferred_date"
      :label="t('wizard.schedule.date')"
      type="date"
      :min="minDate"
      :max="maxDate"
      :hint="t('wizard.schedule.dateHint', { days: MAX_PREFERRED_DAYS_AHEAD })"
      required
      :error="errors.preferred_date"
    />
    <BaseSelect
      v-model="form.time_slot"
      :label="t('wizard.schedule.timeSlot')"
      :options="timeSlotOptions"
      required
      :error="errors.time_slot"
    />
    <div class="step-schedule__row">
      <BaseInput v-model="form.city" :label="t('wizard.schedule.city')" autocomplete="address-level1" required :error="errors.city" />
      <BaseInput v-model="form.district" :label="t('wizard.schedule.district')" autocomplete="address-level2" required :error="errors.district" />
    </div>
    <BaseTextarea
      v-model="form.address"
      :label="t('wizard.schedule.address')"
      :hint="t('wizard.schedule.addressHint')"
      :rows="3"
      required
      :error="errors.address"
    />
  </div>
</template>

<style scoped>
.step-schedule__row {
  display: grid;
  gap: 0 var(--space-4);
}

@media (min-width: 36rem) {
  .step-schedule__row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
