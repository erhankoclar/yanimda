<script setup>
import { computed } from 'vue'

import ServiceIcon from './ServiceIcon.vue'

const selected = defineModel({ type: Number, default: null })

const props = defineProps({
  /** Hizmet: { id, name, description, icon }. */
  service: { type: Object, required: true },
  /** Aynı grupta yalnızca bir kart seçilebilmesi için ortak radyo grubu adı. */
  name: { type: String, required: true },
})

// Kartın seçili görünmesi seçili kimlikten türetilir.
const isSelected = computed(() => selected.value === props.service.id)
</script>

<template>
  <label class="service-card" :class="{ 'service-card--selected': isSelected }">
    <input
      v-model="selected"
      class="service-card__radio"
      type="radio"
      :name="name"
      :value="service.id"
    />
    <span class="service-card__icon"><ServiceIcon :name="service.icon" /></span>
    <span class="service-card__text">
      <span class="service-card__name">{{ service.name }}</span>
      <span class="service-card__description">{{ service.description }}</span>
    </span>
    <span class="service-card__check" aria-hidden="true" />
  </label>
</template>

<style scoped>
.service-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-4);
  min-height: 6rem;
  padding: var(--space-4) var(--space-5);
  border: 2px solid var(--color-line);
  border-radius: var(--radius-card);
  background: var(--color-surface);
  cursor: pointer;
  transition: border-color 150ms ease, background-color 150ms ease;
}

.service-card:hover {
  border-color: var(--color-ink-soft);
}

.service-card:has(.service-card__radio:focus-visible) {
  box-shadow: var(--focus-ring);
}

.service-card--selected,
.service-card--selected:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-tint);
}

/* Radyo düğmesi görsel olarak gizlenir ama klavye ve ekran okuyucu için kalır. */
.service-card__radio {
  position: absolute;
  opacity: 0;
  width: 1px;
  height: 1px;
}

.service-card__icon {
  display: grid;
  place-items: center;
  flex: none;
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  background: var(--color-primary-tint);
  color: var(--color-primary-dark);
}

.service-card--selected .service-card__icon {
  background: var(--color-surface);
}

.service-card__text {
  display: grid;
  gap: var(--space-1);
  flex: 1;
}

.service-card__name {
  font-size: var(--text-lg);
  font-weight: 800;
  line-height: 1.25;
}

.service-card__description {
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}

.service-card__check {
  flex: none;
  width: 1.75rem;
  height: 1.75rem;
  border: 2px solid var(--color-line);
  border-radius: 50%;
  background: var(--color-surface);
}

.service-card--selected .service-card__check {
  border-color: var(--color-ink);
  background: var(--color-ink)
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 12.5 4 4 8-9'/%3E%3C/svg%3E")
    center / 1.1rem no-repeat;
}
</style>
