<script setup>
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { formatDateTime, formatNumber } from '@/admin/format'
import { PAGE_SIZE, useServerTable } from '@/admin/useServerTable'
import { adminApi } from '@/api/admin'

const { t } = useI18n()
const router = useRouter()

const { filters, rows, total, loading, error, first, sortField, sortOrder, onPage, onSort, load } = useServerTable(
  adminApi.users,
  { filters: { search: '', is_staff: '', is_active: '' }, ordering: '-date_joined' },
)

const roleOptions = computed(() => [
  { value: 'false', label: t('admin.users.roles.applicant') },
  { value: 'true', label: t('admin.users.roles.staff') },
])
const activeOptions = computed(() => [
  { value: 'true', label: t('admin.users.active.yes') },
  { value: 'false', label: t('admin.users.active.no') },
])

/**
 * Satıra tıklanınca kullanıcının detayını açar.
 *
 * @param {{ data: { id: number } }} event DataTable satır olayı.
 */
function openRow(event) {
  router.push({ name: 'admin-user-detail', params: { id: event.data.id } })
}
</script>

<template>
  <div class="admin-list">
    <section class="admin-panel admin-list__filters" :aria-label="t('admin.list.filters')">
      <IconField class="admin-list__search">
        <InputIcon class="pi pi-search" />
        <InputText v-model="filters.search" :placeholder="t('admin.users.search')" :aria-label="t('admin.users.search')" fluid />
      </IconField>
      <Select
        v-model="filters.is_staff"
        :options="roleOptions"
        optionLabel="label"
        optionValue="value"
        showClear
        :placeholder="t('admin.users.allRoles')"
        :ariaLabel="t('admin.users.role')"
        class="admin-list__select"
      />
      <Select
        v-model="filters.is_active"
        :options="activeOptions"
        optionLabel="label"
        optionValue="value"
        showClear
        :placeholder="t('admin.users.allAccounts')"
        :ariaLabel="t('admin.users.account')"
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
        :pt="{ table: { 'aria-label': t('admin.titles.users') } }"
        @page="onPage"
        @sort="onSort"
        @rowClick="openRow"
      >
        <template #empty>
          <p class="admin-list__empty">{{ t('admin.list.empty') }}</p>
        </template>
        <Column field="email" :header="t('admin.users.columns.user')" sortable>
          <template #body="{ data }">
            <RouterLink :to="{ name: 'admin-user-detail', params: { id: data.id } }" class="admin-list__link" @click.stop>
              {{ data.full_name || data.email }}
            </RouterLink>
            <span class="admin-list__sub">{{ data.email }}</span>
          </template>
        </Column>
        <Column :header="t('admin.users.columns.phone')">
          <template #body="{ data }">{{ data.phone || t('common.none') }}</template>
        </Column>
        <Column :header="t('admin.users.columns.role')">
          <template #body="{ data }">
            <Tag
              :value="data.is_staff ? t('admin.users.roles.staff') : t('admin.users.roles.applicant')"
              :severity="data.is_staff ? 'info' : 'secondary'"
            />
            <Tag v-if="!data.is_active" :value="t('admin.users.active.no')" severity="danger" class="users__inactive" />
          </template>
        </Column>
        <Column field="request_count" :header="t('admin.users.columns.requests')" sortable>
          <template #body="{ data }">{{ formatNumber(data.request_count) }}</template>
        </Column>
        <Column field="date_joined" :header="t('admin.users.columns.joined')" sortable>
          <template #body="{ data }">{{ formatDateTime(data.date_joined) }}</template>
        </Column>
        <Column :header="t('admin.users.columns.lastLogin')">
          <template #body="{ data }">{{ data.last_login ? formatDateTime(data.last_login) : t('admin.users.never') }}</template>
        </Column>
      </DataTable>
    </section>
  </div>
</template>

<style scoped>
.users__inactive {
  margin-left: 0.35rem;
}
</style>
