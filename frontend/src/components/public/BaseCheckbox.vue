<script setup>
import { useFieldIds } from './useFieldIds'

const model = defineModel({ type: Boolean, default: false })

const props = defineProps({
  error: { type: String, default: '' },
  required: { type: Boolean, default: false },
})

const { inputId, errorId, describedBy } = useFieldIds(() => props)
</script>

<template>
  <div class="checkbox">
    <label class="checkbox__row" :for="inputId">
      <input
        :id="inputId"
        v-model="model"
        class="checkbox__input"
        type="checkbox"
        :required="required"
        :aria-invalid="error ? 'true' : 'false'"
        :aria-describedby="describedBy"
      />
      <span class="checkbox__label"><slot /></span>
    </label>
    <p v-if="error" :id="errorId" class="field__error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.checkbox {
  margin-bottom: var(--space-5);
}

.checkbox__row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 2px solid var(--color-line);
  border-radius: var(--radius-control);
  background: var(--color-surface);
  cursor: pointer;
}

.checkbox__row:has(.checkbox__input:checked) {
  border-color: var(--color-primary);
  background: var(--color-primary-tint);
}

.checkbox__input {
  flex: none;
  width: 1.75rem;
  height: 1.75rem;
  margin: 0;
  accent-color: var(--color-primary);
}

.checkbox__label {
  line-height: 1.45;
}
</style>
