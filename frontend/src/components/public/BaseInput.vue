<script setup>
import { useI18n } from 'vue-i18n'

import { useFieldIds } from './useFieldIds'

// name, maxlength gibi ek öznitelikler kapsayıcıya değil input'a aktarılır.
defineOptions({ inheritAttrs: false })

const model = defineModel({ type: [String, Number], default: '' })

const props = defineProps({
  label: { type: String, required: true },
  type: { type: String, default: 'text' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  required: { type: Boolean, default: false },
  autocomplete: { type: String, default: undefined },
  inputmode: { type: String, default: undefined },
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
    <input
      :id="inputId"
      v-model="model"
      class="field__control"
      :type="type"
      :required="required"
      :autocomplete="autocomplete"
      :inputmode="inputmode"
      :aria-invalid="error ? 'true' : 'false'"
      :aria-describedby="describedBy"
      v-bind="$attrs"
    />
    <p v-if="error" :id="errorId" class="field__error" role="alert">{{ error }}</p>
  </div>
</template>
