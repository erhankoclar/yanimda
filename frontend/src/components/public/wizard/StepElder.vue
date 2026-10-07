<script setup>
import BaseInput from '../BaseInput.vue'
import BaseSelect from '../BaseSelect.vue'
import BaseTextarea from '../BaseTextarea.vue'

import { MAX_ELDER_AGE, MIN_ELDER_AGE, RELATIONSHIP_OPTIONS } from '@/constants/care'

defineProps({
  /** Sihirbaz form nesnesi; alanlar doğrudan güncellenir. */
  form: { type: Object, required: true },
  errors: { type: Object, required: true },
})
</script>

<template>
  <div>
    <BaseInput v-model="form.elder_full_name" label="Adı ve soyadı" autocomplete="off" required :error="errors.elder_full_name" />
    <BaseInput
      v-model="form.elder_age"
      label="Yaşı"
      type="number"
      inputmode="numeric"
      :min="MIN_ELDER_AGE"
      :max="MAX_ELDER_AGE"
      required
      :error="errors.elder_age"
    />
    <BaseSelect
      v-model="form.relationship"
      label="Sizin nesiniz?"
      :options="RELATIONSHIP_OPTIONS"
      required
      :error="errors.relationship"
    />
    <BaseTextarea
      v-model="form.elder_notes"
      label="Bilmemiz gereken bir şey var mı?"
      hint="Örneğin: yürürken desteğe ihtiyaç duyuyor, az işitiyor, şeker hastası."
      :maxlength="1000"
      :error="errors.elder_notes"
    />
  </div>
</template>
