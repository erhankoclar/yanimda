<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import StatCard from '@/components/admin/StatCard.vue'

const props = defineProps({
  /** Dashboard yanıtındaki `cards`; ilk yüklemede null. */
  cards: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const { t } = useI18n()

// Kart sırası: genel talep, bekleyen iş, hızlı talepler, hizmet kapsamı.
const items = computed(() => {
  const cards = props.cards
  return [
    {
      key: 'total-demand',
      icon: 'pi pi-chart-line',
      title: t('admin.dashboard.cards.totalDemand'),
      value: cards?.total_demand.value ?? null,
      change: cards ? cards.total_demand.change_percent : undefined,
    },
    {
      key: 'open-requests',
      icon: 'pi pi-hourglass',
      tone: 'accent',
      title: t('admin.dashboard.cards.openRequests'),
      value: cards?.open_requests.value ?? null,
      note: cards ? t('admin.dashboard.notes.unreviewed', cards.open_requests.new) : '',
    },
    {
      key: 'inquiries',
      icon: 'pi pi-inbox',
      title: t('admin.dashboard.cards.inquiries'),
      value: cards?.inquiries.value ?? null,
      change: cards ? cards.inquiries.change_percent : undefined,
    },
    {
      key: 'services',
      icon: 'pi pi-heart',
      tone: 'accent',
      title: t('admin.dashboard.cards.services'),
      value: cards?.services.value ?? null,
      note: cards?.services.top_service
        ? t('admin.dashboard.notes.topService', { name: cards.services.top_service })
        : t('admin.dashboard.notes.noDemand'),
    },
  ]
})
</script>

<template>
  <section class="dashboard-stats" :aria-label="t('admin.dashboard.cards.label')">
    <StatCard
      v-for="item in items"
      :key="item.key"
      :data-card="item.key"
      :icon="item.icon"
      :tone="item.tone"
      :title="item.title"
      :value="item.value"
      :change="item.change"
      :note="item.note"
      :loading="loading && !cards"
    />
  </section>
</template>

<style scoped>
.dashboard-stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 40rem) {
  .dashboard-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 75rem) {
  .dashboard-stats {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
