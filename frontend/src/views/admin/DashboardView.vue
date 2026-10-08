<script setup>
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useI18n } from 'vue-i18n'

import { useDashboard } from '@/admin/useDashboard'
import DashboardStats from '@/components/admin/dashboard/DashboardStats.vue'

const { t } = useI18n()
const { data, loading, error, load } = useDashboard()
</script>

<template>
  <div class="dashboard">
    <Message v-if="error" severity="error" :closable="false" class="dashboard__error" role="alert">
      <span>{{ error }}</span>
      <Button :label="t('admin.dashboard.retry')" size="small" text @click="load" />
    </Message>

    <DashboardStats :cards="data?.cards ?? null" :loading="loading" />
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
</style>
