<script setup>
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import DatePicker from 'primevue/datepicker'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { formatDateTime, formatShortDate } from '@/admin/format'
import { statusClass, statusSeverity } from '@/admin/status'
import { useFilterOptions } from '@/admin/useFilterOptions'
import { PAGE_SIZE, useServerTable } from '@/admin/useServerTable'
import { adminApi } from '@/api/admin'
import ServiceIcon from '@/components/public/ServiceIcon.vue'
import { STATUS_VALUES, statusLabel } from '@/constants/care'
import { toIsoDate } from '@/utils/dates'

const { t } = useI18n()
const router = useRouter()

const { filters, rows, total, loading, error, first, sortField, sortOrder, onPage, onSort, load } = useServerTable(
  adminApi.requests,
  { filters: { search: '', status: '', service: '', district: '', created_from: '', created_to: '' }, ordering: '-created_at' },
)
const { serviceOptions, districtOptions } = useFilterOptions()

const statusOptions = computed(() => STATUS_VALUES.map((value) => ({ value, label: statusLabel(value) })))

/**
 * `YYYY-MM-DD` metnini yerel gece yarısı tarihine çevirir.
 *
 * @param {string} iso Tarih.
 * @returns {Date | null} Tarih; boşsa null.
 */
function toDate(iso) {
  if (!iso) return null
  const [year, month, day] = iso.split('-').map(Number)
  return new Date(year, month - 1, day)
}

// Tarih aralığı seçicisi URL'deki `created_from` / `created_to` metinleriyle eşlenir.
const dateRange = computed({
  get: () => (filters.created_from ? [toDate(filters.created_from), toDate(filters.created_to)] : null),
  set: (value) => {
    const [from, to] = value ?? []
    filters.created_from = from ? toIsoDate(from) : ''
    // Yalnızca başlangıç seçiliyken bitiş de aynı gündür; ikinci tıklamada güncellenir.
    filters.created_to = to ? toIsoDate(to) : (from ? toIsoDate(from) : '')
  },
})

/**
 * Satıra tıklanınca başvurunun detayını açar.
 *
 * @param {{ data: { id: number } }} event DataTable satır olayı.
 */
function openRow(event) {
  router.push({ name: 'admin-request-detail', params: { id: event.data.id } })
}
</script>

<template>
  <div class="admin-list">
    <section class="admin-panel admin-list__filters admin-list__filters--stacked" :aria-label="t('admin.list.filters')">
      <IconField class="admin-list__search">
        <InputIcon class="pi pi-search" />
        <InputText v-model="filters.search" :placeholder="t('admin.requests.search')" :aria-label="t('admin.requests.search')" fluid />
      </IconField>
      <Select
        v-model="filters.status"
        :options="statusOptions"
        optionLabel="label"
        optionValue="value"
        showClear
        :placeholder="t('admin.list.allStatuses')"
        :ariaLabel="t('admin.list.status')"
        class="admin-list__select"
      />
      <Select
        v-model="filters.service"
        :options="serviceOptions"
        optionLabel="label"
        optionValue="value"
        showClear
        :placeholder="t('admin.list.allServices')"
        :ariaLabel="t('admin.list.service')"
        class="admin-list__select"
      />
      <Select
        v-model="filters.district"
        :options="districtOptions"
        optionLabel="label"
        optionValue="value"
        showClear
        filter
        :placeholder="t('admin.list.allDistricts')"
        :ariaLabel="t('admin.list.district')"
        class="admin-list__select"
      />
      <DatePicker
        v-model="dateRange"
        selectionMode="range"
        :manualInput="false"
        showButtonBar
        showIcon
        :placeholder="t('admin.list.dateRange')"
        :ariaLabel="t('admin.list.dateRange')"
        class="admin-list__select"
      />
    </section>

    <Message v-if="error" severity="error" :closable="false" role="alert" class="admin-list__error">
      <span>{{ error }}</span>
      <Button :label="t('admin.dashboard.retry')" size="small" text @click="load" />
    </Message>

    <section class="admin-panel admin-list__table">
      <DataTable
        :value="rows"
        lazy
        paginator
        :rows="PAGE_SIZE"
        :totalRecords="total"
        :first="first"
        :loading="loading"
        :sortField="sortField"
        :sortOrder="sortOrder"
        removableSort
        dataKey="id"
        rowHover
        size="small"
        :pt="{ table: { 'aria-label': t('admin.titles.requests') } }"
        @page="onPage"
        @sort="onSort"
        @rowClick="openRow"
      >
        <template #empty>
          <p class="admin-list__empty">{{ t('admin.list.empty') }}</p>
        </template>
        <Column field="created_at" :header="t('admin.requests.columns.created')" sortable>
          <template #body="{ data }">{{ formatDateTime(data.created_at) }}</template>
        </Column>
        <Column :header="t('admin.requests.columns.elder')">
          <template #body="{ data }">
            <RouterLink :to="{ name: 'admin-request-detail', params: { id: data.id } }" class="admin-list__link" @click.stop>
              {{ data.elder_full_name }}
            </RouterLink>
            <span class="admin-list__sub">{{ t('admin.requests.age', { age: data.elder_age }) }}</span>
          </template>
        </Column>
        <Column :header="t('admin.requests.columns.service')">
          <template #body="{ data }">
            <span class="admin-list__service"><ServiceIcon :name="data.service.icon" />{{ data.service.name }}</span>
          </template>
        </Column>
        <Column :header="t('admin.requests.columns.location')">
          <template #body="{ data }">
            <template v-if="data.location">
              {{ data.location.neighborhood.name }}
              <span class="admin-list__sub">{{ data.location.district.name }}</span>
            </template>
            <span v-else class="admin-list__sub">{{ t('common.none') }}</span>
          </template>
        </Column>
        <Column field="preferred_date" :header="t('admin.requests.columns.preferred')" sortable>
          <template #body="{ data }">
            {{ formatShortDate(data.preferred_date) }}
            <span class="admin-list__sub">{{ data.time_slot_display }}</span>
          </template>
        </Column>
        <Column :header="t('admin.requests.columns.applicant')">
          <template #body="{ data }">
            {{ data.applicant.full_name || data.applicant.email }}
            <span class="admin-list__sub">{{ data.contact_phone }}</span>
          </template>
        </Column>
        <Column field="status" :header="t('admin.requests.columns.status')" sortable>
          <template #body="{ data }">
            <Tag :value="statusLabel(data.status)" :severity="statusSeverity(data.status)" :class="statusClass(data.status)" />
          </template>
        </Column>
      </DataTable>
    </section>
  </div>
</template>
