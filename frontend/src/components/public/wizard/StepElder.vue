<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseInput from '../BaseInput.vue'
import BaseSelect from '../BaseSelect.vue'
import BaseTextarea from '../BaseTextarea.vue'

import { MAX_ELDER_AGE, MIN_ELDER_AGE, RELATIONSHIP_OPTIONS, localizedOptions } from '@/constants/care'

defineProps({
  /** Sihirbaz form nesnesi; alanlar doğrudan güncellenir. */
  form: { type: Object, required: true },
  errors: { type: Object, required: true },
})

const { t } = useI18n()

// Yakınlık seçenekleri etkin dilde.
const relationshipOptions = computed(() => localizedOptions(RELATIONSHIP_OPTIONS))
</script>

<template>
  <div>
    <BaseInput v-model="form.elder_full_name" :label="t('wizard.elder.name')" autocomplete="off" required :error="errors.elder_full_name" />
    <BaseInput
      v-model="form.elder_age"
      :label="t('wizard.elder.age')"
      type="number"
      inputmode="numeric"
      :min="MIN_ELDER_AGE"
      :max="MAX_ELDER_AGE"
      required
      :error="errors.elder_age"
    />
    <BaseSelect
      v-model="form.relationship"
      :label="t('wizard.elder.relationship')"
      :options="relationshipOptions"
      required
      :error="errors.relationship"
    />
    <BaseTextarea
      v-model="form.elder_notes"
      :label="t('wizard.elder.notes')"
      :hint="t('wizard.elder.notesHint')"
      :maxlength="1000"
      :error="errors.elder_notes"
    />
  </div>
</template>
