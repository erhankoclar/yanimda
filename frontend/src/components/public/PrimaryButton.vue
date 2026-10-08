<script setup>
defineProps({
  /** primary: ana aksiyon, secondary: ikincil aksiyon, ghost: yalnızca metin. */
  variant: { type: String, default: 'primary', validator: (value) => ['primary', 'secondary', 'ghost'].includes(value) },
  type: { type: String, default: 'button' },
  /** true iken düğme kilitlenir ve ekran okuyuculara meşgul olduğu bildirilir. */
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  /** true iken düğme bulunduğu alanın tamamını kaplar. */
  block: { type: Boolean, default: false },
})
</script>

<template>
  <button
    :type="type"
    class="primary-button"
    :class="[`primary-button--${variant}`, { 'primary-button--block': block }]"
    :disabled="disabled || loading"
    :aria-busy="loading ? 'true' : undefined"
  >
    <span v-if="loading" class="primary-button__spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped>
.primary-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  min-height: var(--tap-size);
  padding: var(--space-3) var(--space-6);
  border: 2px solid transparent;
  border-radius: var(--radius-control);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 150ms ease, border-color 150ms ease;
}

.primary-button--block {
  width: 100%;
}

.primary-button--primary {
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.primary-button--primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.primary-button--secondary {
  background: var(--color-surface);
  border-color: var(--color-line);
  color: var(--color-ink);
}

.primary-button--secondary:hover:not(:disabled) {
  border-color: var(--color-ink-soft);
}

.primary-button--ghost {
  background: transparent;
  color: var(--color-primary-dark);
  text-decoration: underline;
  text-underline-offset: 0.2em;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.primary-button__spinner {
  width: 1.1em;
  height: 1.1em;
  border: 3px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
