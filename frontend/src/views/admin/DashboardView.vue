<script setup>
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useI18n } from 'vue-i18n'

import { useDashboard } from '@/admin/useDashboard'
import DashboardStats from '@/components/admin/dashboard/DashboardStats.vue'
import RecentList from '@/components/admin/dashboard/RecentList.vue'
import ServiceTrendChart from '@/components/admin/dashboard/ServiceTrendChart.vue'

const { t } = useI18n()
const { days, source, data, loading, error, load } = useDashboard()
</script>

<template>
  <div class="dashboard">
    <Message v-if="error" severity="error" :closable="false" class="dashboard__error" role="alert">
      <span>{{ error }}</span>
      <Button :label="t('admin.dashboard.retry')" size="small" text @click="load" />
    </Message>

    <DashboardStats :cards="data?.cards ?? null" :loading="loading" />

    <div class="dashboard__row dashboard__row--trend">
      <ServiceTrendChart v-model:days="days" v-model:source="source" :series="data?.series ?? null" :loading="loading" />
      <RecentList :items="data?.recent ?? null" />
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: grid;
  gap: 1.25rem;
}

.dashboard__error :deep(.p-message-text) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.dashboard__row {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1.25rem;
}

/* Geniş ekranda grafik 3/4, son gelenler 1/4 genişlik alır. */
@media (min-width: 75rem) {
  .dashboard__row--trend {
    grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);
  }
}
</style>
