<script setup>
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Skeleton from 'primevue/skeleton'
import Tag from 'primevue/tag'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { formatRelativeTime, formatShortDate } from '@/admin/format'
import { statusClass, statusSeverity } from '@/admin/status'
import ServiceIcon from '@/components/public/ServiceIcon.vue'
import { statusLabel } from '@/constants/care'

defineProps({
  /** Dashboard yanıtındaki `pending`: en eski açık başvurular; ilk yüklemede null. */
  items: { type: Array, default: null },
})

const { t } = useI18n()
const router = useRouter()

/**
 * Satıra tıklanınca başvurunun detayını açar; klavye için yaşlı adı ayrıca bağlantıdır.
 *
 * @param {{ data: { id: number } }} event DataTable satır olayı.
 */
function openRow(event) {
  router.push({ name: 'admin-request-detail', params: { id: event.data.id } })
}
</script>

<template>
  <section class="admin-panel pending" aria-labelledby="pending-title">
    <div class="admin-panel__head">
      <h2 id="pending-title">{{ t('admin.dashboard.pending.title') }}</h2>
      <RouterLink :to="{ name: 'admin-requests' }" class="pending__all">
        {{ t('admin.dashboard.pending.viewAll') }}
      </RouterLink>
    </div>

    <div v-if="!items" aria-hidden="true">
      <Skeleton v-for="index in 4" :key="index" height="2.5rem" class="pending__skeleton" />
    </div>
    <p v-else-if="!items.length" class="pending__empty">{{ t('admin.dashboard.pending.empty') }}</p>
    <DataTable
      v-else
      :value="items"
      dataKey="id"
      size="small"
      rowHover
      class="pending__table"
      :pt="{ table: { 'aria-labelledby': 'pending-title' } }"
      @rowClick="openRow"
    >
      <Column :header="t('admin.dashboard.pending.columns.elder')">
        <template #body="{ data }">
          <RouterLink :to="{ name: 'admin-request-detail', params: { id: data.id } }" class="pending__elder" @click.stop>
            {{ data.elder_full_name }}
          </RouterLink>
        </template>
      </Column>
      <Column :header="t('admin.dashboard.pending.columns.service')" bodyClass="pending__service-cell">
        <template #body="{ data }">
          <span class="pending__service">
            <ServiceIcon :name="data.service.icon" />
            {{ data.service.name }}
          </span>
        </template>
      </Column>
      <Column :header="t('admin.dashboard.pending.columns.preferredDate')">
        <template #body="{ data }">{{ formatShortDate(data.preferred_date) }}</template>
      </Column>
      <Column :header="t('admin.dashboard.pending.columns.waiting')">
        <template #body="{ data }">
          <time :datetime="data.created_at">{{ formatRelativeTime(data.created_at) }}</time>
        </template>
      </Column>
      <Column :header="t('admin.dashboard.pending.columns.status')">
        <template #body="{ data }">
          <Tag :value="statusLabel(data.status)" :severity="statusSeverity(data.status)" :class="statusClass(data.status)" />
        </template>
      </Column>
    </DataTable>
  </section>
</template>

<style scoped>
.pending {
  min-width: 0;
}

.pending__all {
  color: var(--admin-primary);
  font-weight: 700;
  text-decoration: none;
}

.pending__all:hover {
  text-decoration: underline;
}

/* Dar ekranda tablo kendi içinde kayar; sayfa yatay taşmaz. */
.pending__table {
  overflow-x: auto;
}

.pending__table :deep(tr) {
  cursor: pointer;
}

.pending__table :deep(td),
.pending__table :deep(th) {
  white-space: nowrap;
}

/* Uzun hizmet adları alt satıra geçer; durum sütunu panelin dışına itilmez. */
.pending__table :deep(td.pending__service-cell) {
  white-space: normal;
}

.pending__elder {
  color: inherit;
  font-weight: 700;
  text-decoration: none;
}

.pending__elder:hover,
.pending__elder:focus-visible {
  color: var(--admin-primary);
  text-decoration: underline;
}

.pending__service {
  display: inline-flex;
  align-items: flex-start;
  gap: 0.4rem;
}

.pending__service :deep(.service-icon) {
  flex: none;
  width: 1.15rem;
  height: 1.15rem;
  color: var(--admin-primary);
}

.pending__skeleton {
  margin-bottom: 0.5rem;
}

.pending__empty {
  margin: 0;
  color: var(--admin-ink-soft);
}
</style>
