<script setup>
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'
import Tag from 'primevue/tag'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { formatDateTime, formatNumber, formatShortDate } from '@/admin/format'
import { statusClass, statusSeverity } from '@/admin/status'
import { PAGE_SIZE, useServerTable } from '@/admin/useServerTable'
import { adminApi } from '@/api/admin'
import ServiceIcon from '@/components/public/ServiceIcon.vue'
import { statusLabel } from '@/constants/care'
import { parseApiError } from '@/utils/apiErrors'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const { t } = useI18n()
const router = useRouter()

const user = ref(null)
const loadError = ref('')
const notFound = ref(false)

/** Kullanıcı profilini yükler. */
async function loadUser() {
  loadError.value = ''
  notFound.value = false
  try {
    user.value = await adminApi.user(props.id)
  } catch (failure) {
    if (failure?.response?.status === 404) notFound.value = true
    else loadError.value = parseApiError(failure).general
  }
}

watch(() => props.id, loadUser, { immediate: true })

// Kullanıcının başvuruları admin başvuru listesinden `applicant` süzgeciyle gelir.
const requests = useServerTable(
  (params) => adminApi.requests({ ...params, applicant: props.id }),
  { ordering: '-created_at' },
)

/**
 * Başvuru satırına tıklanınca detayını açar.
 *
 * @param {{ data: { id: number } }} event DataTable satır olayı.
 */
function openRequest(event) {
  router.push({ name: 'admin-request-detail', params: { id: event.data.id } })
}
</script>

<template>
  <div class="user-detail">
    <RouterLink :to="{ name: 'admin-users' }" class="user-detail__back">
      <i class="pi pi-arrow-left" aria-hidden="true" />
      {{ t('admin.userDetail.back') }}
    </RouterLink>

    <Message v-if="notFound" severity="warn" :closable="false">{{ t('admin.userDetail.notFound') }}</Message>
    <Message v-else-if="loadError" severity="error" :closable="false" role="alert" class="admin-list__error">
      <span>{{ loadError }}</span>
      <Button :label="t('admin.dashboard.retry')" size="small" text @click="loadUser" />
    </Message>
    <Skeleton v-else-if="!user" height="9rem" />

    <section v-else class="admin-panel user-detail__profile" aria-labelledby="user-name">
      <span class="user-detail__avatar" aria-hidden="true"><i class="pi pi-user" /></span>
      <div class="user-detail__main">
        <h2 id="user-name">{{ user.full_name || user.email }}</h2>
        <div class="user-detail__tags">
          <Tag :value="user.is_staff ? t('admin.users.roles.staff') : t('admin.users.roles.applicant')" :severity="user.is_staff ? 'info' : 'secondary'" />
          <Tag :value="user.is_active ? t('admin.users.active.yes') : t('admin.users.active.no')" :severity="user.is_active ? 'success' : 'danger'" />
        </div>
      </div>
      <dl class="user-detail__facts">
        <div class="user-detail__email"><dt>{{ t('admin.users.columns.email') }}</dt><dd><a :href="`mailto:${user.email}`">{{ user.email }}</a></dd></div>
        <div><dt>{{ t('admin.users.columns.phone') }}</dt><dd>{{ user.phone || t('common.none') }}</dd></div>
        <div><dt>{{ t('admin.users.columns.joined') }}</dt><dd>{{ formatDateTime(user.date_joined) }}</dd></div>
        <div><dt>{{ t('admin.users.columns.lastLogin') }}</dt><dd>{{ user.last_login ? formatDateTime(user.last_login) : t('admin.users.never') }}</dd></div>
        <div><dt>{{ t('admin.users.columns.requests') }}</dt><dd>{{ formatNumber(user.request_count) }}</dd></div>
      </dl>
    </section>

    <section class="admin-panel admin-list__table" aria-labelledby="user-requests-title">
      <h2 id="user-requests-title" class="user-detail__title">{{ t('admin.userDetail.requests') }}</h2>
      <Message v-if="requests.error.value" severity="error" :closable="false" role="alert">{{ requests.error.value }}</Message>
      <DataTable
        :value="requests.rows.value"
        lazy
        paginator
        :rows="PAGE_SIZE"
        :totalRecords="requests.total.value"
        :first="requests.first.value"
        :loading="requests.loading.value"
        dataKey="id"
        rowHover
        size="small"
        :pt="{ table: { 'aria-labelledby': 'user-requests-title' } }"
        @page="requests.onPage"
        @rowClick="openRequest"
      >
        <template #empty>
          <p class="admin-list__empty">{{ t('admin.userDetail.noRequests') }}</p>
        </template>
        <Column :header="t('admin.requests.columns.created')">
          <template #body="{ data }">{{ formatDateTime(data.created_at) }}</template>
        </Column>
        <Column :header="t('admin.requests.columns.elder')">
          <template #body="{ data }">
            <RouterLink :to="{ name: 'admin-request-detail', params: { id: data.id } }" class="admin-list__link" @click.stop>
              {{ data.elder_full_name }}
            </RouterLink>
          </template>
        </Column>
        <Column :header="t('admin.requests.columns.service')">
          <template #body="{ data }">
            <span class="admin-list__service"><ServiceIcon :name="data.service.icon" />{{ data.service.name }}</span>
          </template>
        </Column>
        <Column :header="t('admin.requests.columns.preferred')">
          <template #body="{ data }">{{ formatShortDate(data.preferred_date) }}</template>
        </Column>
        <Column :header="t('admin.requests.columns.status')">
          <template #body="{ data }"><Tag :value="statusLabel(data.status)" :severity="statusSeverity(data.status)" :class="statusClass(data.status)" /></template>
        </Column>
      </DataTable>
    </section>
  </div>
</template>

<style scoped>
.user-detail {
  display: grid;
  gap: 1rem;
}

.user-detail__back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  width: fit-content;
  color: var(--admin-ink-soft);
  font-weight: 700;
  text-decoration: none;
}

.user-detail__back:hover {
  color: var(--admin-primary);
}

.user-detail__profile {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 1rem;
  align-items: center;
}

.user-detail__avatar {
  display: inline-grid;
  place-items: center;
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 50%;
  background: var(--admin-primary-tint);
  color: var(--admin-primary);
  font-size: 1.3rem;
}

.user-detail__main h2 {
  font-size: 1.3rem;
  overflow-wrap: anywhere;
}

.user-detail__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.35rem;
}

.user-detail__facts {
  display: grid;
  grid-column: 1 / -1;
  grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
  gap: 0.75rem 1.25rem;
  margin: 0;
  padding-top: 1rem;
  border-top: 1px solid var(--admin-line);
}

/* E-posta bölünmesin diye geniş ekranda iki sütun kaplar. */
@media (min-width: 48rem) {
  .user-detail__email {
    grid-column: span 2;
  }
}

.user-detail__facts dt {
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
  font-weight: 700;
}

.user-detail__facts dd {
  margin: 0.1rem 0 0;
  overflow-wrap: anywhere;
}

.user-detail__facts a {
  color: var(--admin-primary);
  font-weight: 700;
}

.user-detail__title {
  margin: 0.25rem 0.5rem 0.75rem;
  font-size: 1rem;
}
</style>
