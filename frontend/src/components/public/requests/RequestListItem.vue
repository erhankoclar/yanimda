<script setup>
import ServiceIcon from '../ServiceIcon.vue'
import StatusBadge from './StatusBadge.vue'

import { TIME_SLOT_OPTIONS, optionLabel } from '@/constants/care'
import { formatLongDate } from '@/utils/dates'

defineProps({
  /** Başvuru: API'nin döndürdüğü talep nesnesi. */
  request: { type: Object, required: true },
})
</script>

<template>
  <RouterLink class="request-item" :to="{ name: 'request-detail', params: { id: request.id } }">
    <span class="request-item__icon"><ServiceIcon :name="request.service_detail.icon" /></span>
    <span class="request-item__body">
      <span class="request-item__title">{{ request.service_detail.name }}</span>
      <span class="request-item__meta">{{ request.elder_full_name }} için</span>
      <span class="request-item__meta">
        {{ formatLongDate(request.preferred_date) }}, {{ optionLabel(TIME_SLOT_OPTIONS, request.time_slot) }}
      </span>
    </span>
    <StatusBadge :status="request.status" class="request-item__status" />
  </RouterLink>
</template>

<style scoped>
.request-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--space-2) var(--space-4);
  padding: var(--space-4) var(--space-5);
  border: 2px solid var(--color-line);
  border-radius: var(--radius-card);
  background: var(--color-surface);
  color: var(--color-ink);
  text-decoration: none;
}

.request-item:hover {
  border-color: var(--color-ink-soft);
}

.request-item__icon {
  display: grid;
  place-items: center;
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  background: var(--color-linden-tint);
  color: var(--color-linden-dark);
}

.request-item__icon :deep(svg) {
  width: 2.25rem;
  height: 2.25rem;
}

.request-item__body {
  display: grid;
  gap: var(--space-1);
}

.request-item__title {
  font-size: var(--text-lg);
  font-weight: 800;
  line-height: 1.25;
}

.request-item__meta {
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}

.request-item__status {
  grid-column: 2;
  justify-self: start;
}

@media (min-width: 36rem) {
  .request-item {
    grid-template-columns: auto 1fr auto;
    align-items: center;
  }

  .request-item__status {
    grid-column: auto;
  }
}
</style>
