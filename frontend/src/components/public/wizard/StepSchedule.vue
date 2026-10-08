<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseInput from '../BaseInput.vue'
import BaseSelect from '../BaseSelect.vue'
import BaseTextarea from '../BaseTextarea.vue'
import LocationFields from '../LocationFields.vue'

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
    <LocationFields v-model:district="form.district" v-model:neighborhood="form.neighborhood" :errors="errors" />
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

