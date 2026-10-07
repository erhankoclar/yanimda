<script setup>
import { computed } from 'vue'

import { STATUS_LABELS } from '@/constants/care'

const props = defineProps({
  status: { type: String, required: true },
})

// Arayüz dilindeki durum etiketi; bilinmeyen durumda değerin kendisi gösterilir.
const label = computed(() => STATUS_LABELS[props.status] ?? props.status)
</script>

<template>
  <span class="status-badge" :class="`status-badge--${status}`">{{ label }}</span>
</template>

<style scoped>
.status-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: 999px;
  font-size: var(--text-sm);
  font-weight: 700;
  white-space: nowrap;
}

.status-badge--new {
  background: var(--color-linden-tint);
  color: var(--color-linden-dark);
}

.status-badge--reviewing,
.status-badge--assigned {
  background: var(--color-honey-tint);
  color: #6b4a06;
}

.status-badge--completed {
  background: var(--color-linden-dark);
  color: #fff;
}

.status-badge--cancelled {
  background: var(--color-line);
  color: var(--color-ink-soft);
}
</style>
