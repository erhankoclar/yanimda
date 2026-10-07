<script setup>
defineProps({
  /** Gösterilecek mesaj; boşsa bileşen hiçbir şey çizmez. */
  message: { type: String, default: '' },
})
</script>

<template>
  <div v-if="message" class="form-alert" role="alert">
    <svg class="form-alert__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M12 3 2 20h20L12 3Z" />
      <path d="M12 10v4" />
      <path d="M12 17.5v.01" />
    </svg>
    <p>{{ message }}</p>
  </div>
</template>

<style scoped>
.form-alert {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  margin-bottom: var(--space-5);
  padding: var(--space-4);
  border-left: 4px solid var(--color-danger);
  border-radius: var(--radius-control);
  background: var(--color-danger-tint);
  color: var(--color-ink);
}

.form-alert p {
  margin: 0;
}

.form-alert__icon {
  flex: none;
  width: 1.5rem;
  height: 1.5rem;
  margin-top: 0.1rem;
  fill: none;
  stroke: var(--color-danger);
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
