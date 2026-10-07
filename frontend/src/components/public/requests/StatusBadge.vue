<script setup>
import { computed } from 'vue'

import { statusLabel } from '@/constants/care'

const props = defineProps({
  status: { type: String, required: true },
})

// Arayüz dilindeki durum etiketi; bilinmeyen durumda değerin kendisi gösterilir.
const label = computed(() => statusLabel(props.status))
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
  background: var(--color-primary-tint);
  color: var(--color-primary-dark);
}

.status-badge--reviewing,
.status-badge--assigned {
  background: var(--color-accent-tint);
  color: var(--color-accent-ink);
}

.status-badge--completed {
  background: var(--color-primary-dark);
  color: var(--color-on-primary);
}

.status-badge--cancelled {
  background: var(--color-line);
  color: var(--color-ink-soft);
}
</style>
