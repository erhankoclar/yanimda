<script setup>
import { useI18n } from 'vue-i18n'

import { useFieldIds } from './useFieldIds'

const model = defineModel({ type: [String, Number], default: '' })

const props = defineProps({
  label: { type: String, required: true },
  /** Seçenekler: [{ value, label }]. */
  options: { type: Array, required: true },
  /** Boşsa ortak "Seçin" metni kullanılır. */
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  required: { type: Boolean, default: false },
})

const { t } = useI18n()
const { inputId, hintId, errorId, describedBy } = useFieldIds(() => props)
</script>

<template>
  <div class="field">
    <label class="field__label" :for="inputId">
      {{ label }}
      <span v-if="!required" class="field__optional">{{ t('common.optional') }}</span>
    </label>
    <p v-if="hint" :id="hintId" class="field__hint">{{ hint }}</p>
    <select
      :id="inputId"
      v-model="model"
      class="field__control"
      :required="required"
      :aria-invalid="error ? 'true' : 'false'"
      :aria-describedby="describedBy"
    >
      <option value="" disabled>{{ placeholder || t('common.select') }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">{{ option.label }}</option>
    </select>
    <p v-if="error" :id="errorId" class="field__error" role="alert">{{ error }}</p>
  </div>
</template>
