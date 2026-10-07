<script setup>
import BaseInput from '../BaseInput.vue'
import BaseSelect from '../BaseSelect.vue'
import BaseTextarea from '../BaseTextarea.vue'

import { MAX_PREFERRED_DAYS_AHEAD, TIME_SLOT_OPTIONS } from '@/constants/care'
import { isoDateAfter, toIsoDate } from '@/utils/dates'

defineProps({
  form: { type: Object, required: true },
  errors: { type: Object, required: true },
})

const minDate = toIsoDate(new Date())
const maxDate = isoDateAfter(MAX_PREFERRED_DAYS_AHEAD)
</script>

<template>
  <div>
    <BaseInput
      v-model="form.preferred_date"
      label="Hangi gün?"
      type="date"
      :min="minDate"
      :max="maxDate"
      :hint="`Bugünden itibaren ${MAX_PREFERRED_DAYS_AHEAD} gün içinde bir gün seçebilirsiniz.`"
      required
      :error="errors.preferred_date"
    />
    <BaseSelect
      v-model="form.time_slot"
      label="Günün hangi saatleri?"
      :options="TIME_SLOT_OPTIONS"
      required
      :error="errors.time_slot"
    />
    <div class="step-schedule__row">
      <BaseInput v-model="form.city" label="İl" autocomplete="address-level1" required :error="errors.city" />
      <BaseInput v-model="form.district" label="İlçe" autocomplete="address-level2" required :error="errors.district" />
    </div>
    <BaseTextarea
      v-model="form.address"
      label="Açık adres"
      hint="Mahalle, sokak, bina ve daire numarası."
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
