<script setup>
import { computed } from 'vue'

import { useFieldIds } from './useFieldIds'

const model = defineModel({ type: String, default: '' })

const props = defineProps({
  label: { type: String, required: true },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  required: { type: Boolean, default: false },
  rows: { type: Number, default: 4 },
  /** Verilirse kalan karakter sayısı gösterilir. */
  maxlength: { type: Number, default: undefined },
})

const { inputId, hintId, errorId, describedBy } = useFieldIds(() => props)

// Kullanıcıya kaç karakter hakkı kaldığını gösterir.
const remaining = computed(() => (props.maxlength ? props.maxlength - (model.value?.length ?? 0) : null))
</script>

<template>
  <div class="field">
    <label class="field__label" :for="inputId">
      {{ label }}
      <span v-if="!required" class="field__optional">(isteğe bağlı)</span>
    </label>
    <p v-if="hint" :id="hintId" class="field__hint">{{ hint }}</p>
    <textarea
      :id="inputId"
      v-model="model"
      class="field__control"
      :rows="rows"
      :required="required"
      :maxlength="maxlength"
      :aria-invalid="error ? 'true' : 'false'"
      :aria-describedby="describedBy"
    />
    <p v-if="remaining !== null" class="field__hint">{{ remaining }} karakter kaldı</p>
    <p v-if="error" :id="errorId" class="field__error" role="alert">{{ error }}</p>
  </div>
</template>
