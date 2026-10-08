<script setup>
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

import { formatDateTime } from '@/admin/format'
import { useFilterOptions } from '@/admin/useFilterOptions'
import { PAGE_SIZE, useServerTable } from '@/admin/useServerTable'
import { adminApi } from '@/api/admin'
import InquiryDrawer from '@/components/admin/inquiries/InquiryDrawer.vue'
import ServiceIcon from '@/components/public/ServiceIcon.vue'
import { parseApiError } from '@/utils/apiErrors'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const table = useServerTable(adminApi.inquiries, { filters: { search: '', service: '', district: '' } })
const { filters, rows, total, loading, error, first, onPage, load } = table
const { serviceOptions, districtOptions } = useFilterOptions()

const selected = ref(null)
const drawerOpen = ref(false)
const drawerError = ref('')

/**
 * Talebin ayrıntısını çekmecede açar ve adresi `?id=` ile paylaşılabilir yapar.
 *
 * @param {{ data: { id: number } }} event DataTable satır olayı.
 */
function openRow(event) {
  selected.value = event.data
  drawerOpen.value = true
  router.replace({ query: { ...route.query, id: event.data.id } })
}

// Gösterge panelinden veya haritadan `?id=` ile gelindiğinde talep sunucudan okunup açılır.
watch(() => route.query.id, async (id) => {
  if (!id) return
  if (selected.value?.id === Number(id)) return
  drawerError.value = ''
  try {
    selected.value = await adminApi.inquiry(id)
    drawerOpen.value = true
  } catch (failure) {
    drawerError.value = failure?.response?.status === 404 ? t('admin.inquiries.notFound') : parseApiError(failure).general
  }
}, { immediate: true })

// Çekmece kapanınca adresteki `id` kaldırılır.
watch(drawerOpen, (open) => {
  if (open || !route.query.id) return
  const query = { ...route.query }
  delete query.id
  router.replace({ query })
})
</script>

<template>
  <div class="admin-list">
    <section class="admin-panel admin-list__filters" :aria-label="t('admin.list.filters')">
      <IconField class="admin-list__search">
        <InputIcon class="pi pi-search" />
        <InputText v-model="filters.search" :placeholder="t('admin.inquiries.search')" :aria-label="t('admin.inquiries.search')" fluid />
      </IconField>
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
    </section>

    <Message v-if="error || drawerError" severity="error" :closable="false" role="alert" class="admin-list__error">
      <span>{{ error || drawerError }}</span>
      <Button v-if="error" :label="t('admin.dashboard.retry')" size="small" text @click="load" />
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
        dataKey="id"
        rowHover
        size="small"
        :pt="{ table: { 'aria-label': t('admin.titles.inquiries') } }"
        @page="onPage"
        @rowClick="openRow"
      >
        <template #empty>
          <p class="admin-list__empty">{{ t('admin.list.empty') }}</p>
        </template>
        <Column :header="t('admin.inquiries.columns.created')">
          <template #body="{ data }">{{ formatDateTime(data.created_at) }}</template>
        </Column>
        <Column :header="t('admin.inquiries.columns.name')">
          <template #body="{ data }">
            <button type="button" class="admin-list__link" @click.stop="openRow({ data })">{{ data.full_name }}</button>
            <span class="admin-list__sub">{{ data.email }}</span>
          </template>
        </Column>
        <Column :header="t('admin.inquiries.columns.service')">
          <template #body="{ data }">
            <span class="admin-list__service"><ServiceIcon :name="data.service.icon" />{{ data.service.name }}</span>
          </template>
        </Column>
        <Column :header="t('admin.inquiries.columns.location')">
          <template #body="{ data }">
            <template v-if="data.location">
              {{ data.location.neighborhood.name }}
              <span class="admin-list__sub">{{ data.location.district.name }}</span>
            </template>
            <span v-else class="admin-list__sub">{{ t('common.none') }}</span>
          </template>
        </Column>
        <Column :header="t('admin.inquiries.columns.message')" bodyClass="admin-list__wrap">
          <template #body="{ data }"><span class="admin-list__preview">{{ data.message }}</span></template>
        </Column>
      </DataTable>
    </section>

    <InquiryDrawer v-model:visible="drawerOpen" :inquiry="selected" />
  </div>
</template>
