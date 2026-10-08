<script setup>
import Button from 'primevue/button'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { formatDateTime } from '@/admin/format'
import { adminApi } from '@/api/admin'
import RequestStatusPanel from '@/components/admin/requests/RequestStatusPanel.vue'
import ServiceIcon from '@/components/public/ServiceIcon.vue'
import { statusLabel } from '@/constants/care'
import { i18n } from '@/i18n'
import { parseApiError } from '@/utils/apiErrors'
import { formatLongDate } from '@/utils/dates'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const { t } = useI18n()
const confirm = useConfirm()
const toast = useToast()

const request = ref(null)
const loadError = ref('')
const notFound = ref(false)
const saving = ref(false)
const fieldErrors = ref({})

/** Başvuruyu yükler; bulunamazsa ayrı bir durum gösterilir. */
async function load() {
  loadError.value = ''
  notFound.value = false
  try {
    request.value = await adminApi.request(props.id)
  } catch (failure) {
    if (failure?.response?.status === 404) notFound.value = true
    else loadError.value = parseApiError(failure).general
  }
}

watch(() => props.id, load, { immediate: true })
// Hizmet ve durum etiketleri dile göre döndüğü için dil değişince yeniden yüklenir.
watch(i18n.global.locale, load)

/**
 * Değişiklikleri kaydeder; durum değişiyorsa önce onay ister.
 *
 * @param {{ status?: string, admin_note?: string }} changes Değişen alanlar.
 */
function save(changes) {
  fieldErrors.value = {}
  if (!changes.status) {
    submit(changes)
    return
  }
  confirm.require({
    header: t('admin.requestDetail.confirmTitle'),
    message: t('admin.requestDetail.confirmText', { from: statusLabel(request.value.status), to: statusLabel(changes.status) }),
    icon: 'pi pi-question-circle',
    acceptProps: { label: t('admin.requestDetail.confirmAccept') },
    rejectProps: { label: t('admin.requestDetail.confirmReject'), severity: 'secondary', outlined: true },
    accept: () => submit(changes),
  })
}

/**
 * PATCH isteğini gönderir; başarıda bildirim gösterir, 400'de alan hatalarını yazar.
 *
 * @param {{ status?: string, admin_note?: string }} changes Değişen alanlar.
 */
async function submit(changes) {
  saving.value = true
  try {
    request.value = await adminApi.updateRequest(props.id, changes)
    toast.add({ severity: 'success', summary: t('admin.requestDetail.saved'), life: 3500 })
  } catch (failure) {
    const parsed = parseApiError(failure, ['status', 'admin_note'])
    fieldErrors.value = parsed.fields
    if (parsed.general) toast.add({ severity: 'error', summary: parsed.general, life: 5000 })
  } finally {
    saving.value = false
  }
}

// Bilgi kartları; her biri başlık ve satırlardan oluşur.
const sections = computed(() => {
  const item = request.value
  if (!item) return []
  const none = t('common.none')
  return [
    {
      key: 'elder',
      title: t('admin.requestDetail.sections.elder'),
      rows: [
        [t('admin.requestDetail.rows.name'), item.elder_full_name],
        [t('admin.requestDetail.rows.age'), item.elder_age],
        [t('admin.requestDetail.rows.relationship'), item.relationship_display],
        [t('admin.requestDetail.rows.notes'), item.elder_notes || none],
      ],
    },
    {
      key: 'schedule',
      title: t('admin.requestDetail.sections.schedule'),
      rows: [
        [t('admin.requestDetail.rows.date'), formatLongDate(item.preferred_date)],
        [t('admin.requestDetail.rows.time'), item.time_slot_display],
        [t('admin.requestDetail.rows.location'), item.location ? `${item.location.neighborhood.name}, ${item.location.district.name}` : none],
        [t('admin.requestDetail.rows.address'), item.address],
      ],
    },
    {
      key: 'contact',
      title: t('admin.requestDetail.sections.contact'),
      rows: [
        [t('admin.requestDetail.rows.phone'), item.contact_phone],
        [t('admin.requestDetail.rows.alternate'), item.alternate_contact_name ? `${item.alternate_contact_name}, ${item.alternate_contact_phone}` : none],
        [t('admin.requestDetail.rows.consent'), formatDateTime(item.consent_given_at)],
      ],
    },
  ]
})
</script>

<template>
  <div class="request-detail">
    <RouterLink :to="{ name: 'admin-requests' }" class="request-detail__back">
      <i class="pi pi-arrow-left" aria-hidden="true" />
      {{ t('admin.requestDetail.back') }}
    </RouterLink>

    <Message v-if="notFound" severity="warn" :closable="false">{{ t('admin.requestDetail.notFound') }}</Message>
    <Message v-else-if="loadError" severity="error" :closable="false" role="alert" class="admin-list__error">
      <span>{{ loadError }}</span>
      <Button :label="t('admin.dashboard.retry')" size="small" text @click="load" />
    </Message>

    <div v-else-if="!request" class="request-detail__grid" aria-hidden="true">
      <Skeleton height="16rem" />
      <Skeleton height="16rem" />
    </div>

    <template v-else>
      <header class="admin-panel request-detail__head">
        <span class="request-detail__icon"><ServiceIcon :name="request.service.icon" /></span>
        <div>
          <h2>{{ request.service.name }}</h2>
          <p>{{ t('admin.requestDetail.meta', { id: request.id, created: formatDateTime(request.created_at), updated: formatDateTime(request.updated_at) }) }}</p>
        </div>
      </header>

      <div class="request-detail__grid">
        <div class="request-detail__cards">
          <section v-for="section in sections" :key="section.key" class="admin-panel" :aria-labelledby="`section-${section.key}`">
            <h2 :id="`section-${section.key}`" class="request-detail__title">{{ section.title }}</h2>
            <dl class="request-detail__rows">
              <div v-for="[label, value] in section.rows" :key="label">
                <dt>{{ label }}</dt>
                <dd>{{ value }}</dd>
              </div>
            </dl>
          </section>

          <section class="admin-panel" aria-labelledby="section-applicant">
            <h2 id="section-applicant" class="request-detail__title">{{ t('admin.requestDetail.sections.applicant') }}</h2>
            <dl class="request-detail__rows">
              <div>
                <dt>{{ t('admin.requestDetail.rows.name') }}</dt>
                <dd>
                  <RouterLink :to="{ name: 'admin-user-detail', params: { id: request.applicant.id } }">
                    {{ request.applicant.full_name || request.applicant.email }}
                  </RouterLink>
                </dd>
              </div>
              <div>
                <dt>{{ t('admin.requestDetail.rows.email') }}</dt>
                <dd><a :href="`mailto:${request.applicant.email}`">{{ request.applicant.email }}</a></dd>
              </div>
              <div>
                <dt>{{ t('admin.requestDetail.rows.profilePhone') }}</dt>
                <dd>{{ request.applicant.phone || t('common.none') }}</dd>
              </div>
            </dl>
          </section>
        </div>

        <RequestStatusPanel :request="request" :errors="fieldErrors" :saving="saving" @save="save" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.request-detail {
  display: grid;
  gap: 1rem;
}

.request-detail__back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  width: fit-content;
  color: var(--admin-ink-soft);
  font-weight: 700;
  text-decoration: none;
}

.request-detail__back:hover {
  color: var(--admin-primary);
}

.request-detail__head {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.request-detail__head h2 {
  font-size: 1.2rem;
}

.request-detail__head p {
  margin: 0.15rem 0 0;
  color: var(--admin-ink-soft);
  font-size: 0.85rem;
}

.request-detail__icon {
  display: inline-grid;
  flex: none;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 50%;
  background: var(--admin-primary-tint);
  color: var(--admin-primary);
}

.request-detail__icon :deep(.service-icon) {
  width: 1.5rem;
  height: 1.5rem;
}

.request-detail__grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
  align-items: start;
}

.request-detail__cards {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
}

.request-detail__title {
  margin-bottom: 0.75rem;
  font-size: 1rem;
}

.request-detail__rows {
  display: grid;
  gap: 0.6rem;
  margin: 0;
}

.request-detail__rows dt {
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
  font-weight: 700;
}

.request-detail__rows dd {
  margin: 0.1rem 0 0;
  overflow-wrap: anywhere;
}

.request-detail__rows a {
  color: var(--admin-primary);
  font-weight: 700;
}

@media (min-width: 48rem) {
  .request-detail__cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 75rem) {
  .request-detail__grid {
    grid-template-columns: minmax(0, 2fr) minmax(18rem, 1fr);
  }

  /* Durum paneli kaydırırken görünür kalır. */
  .request-detail__grid > :last-child {
    position: sticky;
    top: 5.5rem;
  }
}
</style>
