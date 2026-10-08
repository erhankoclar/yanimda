<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import { requestsApi } from '@/api/requests'
import StatusBadge from '@/components/public/requests/StatusBadge.vue'
import StatusTimeline from '@/components/public/requests/StatusTimeline.vue'
import { RELATIONSHIP_OPTIONS, TIME_SLOT_OPTIONS, optionLabel } from '@/constants/care'
import { formatLongDate } from '@/utils/dates'

const { t } = useI18n()

const props = defineProps({
  id: { type: String, required: true },
})

const route = useRoute()
const request = ref(null)
const status = ref('loading')

// Sihirbazdan yeni gelindiyse başarı mesajı gösterilir.
const justCreated = computed(() => route.query.created === '1')

// Başvuru ayrıntıları ekranda gösterilecek satırlara çevrilir.
const rows = computed(() => {
  const item = request.value
  if (!item) return []
  return [
    [t('requests.detail.elder'), t('requests.detail.elderValue', { name: item.elder_full_name, age: item.elder_age })],
    [t('requests.detail.relationship'), optionLabel(RELATIONSHIP_OPTIONS, item.relationship)],
    [t('requests.detail.date'), `${formatLongDate(item.preferred_date)}, ${optionLabel(TIME_SLOT_OPTIONS, item.time_slot)}`],
    // Konum alanından önceki kayıtlarda mahalle yoktur.
    [t('requests.detail.location'), item.location ? `${item.location.neighborhood.name}, ${item.location.district.name}` : t('common.none')],
    [t('requests.detail.address'), item.address],
    [t('requests.detail.phone'), item.contact_phone],
    [t('requests.detail.alternate'), item.alternate_contact_name ? `${item.alternate_contact_name}, ${item.alternate_contact_phone}` : t('common.none')],
    [t('requests.detail.notes'), item.elder_notes || t('common.none')],
  ]
})

/** Başvuruyu yükler; bulunamazsa veya hata olursa ilgili durumu gösterir. */
async function load() {
  status.value = 'loading'
  try {
    request.value = await requestsApi.get(props.id)
    status.value = 'ready'
  } catch (error) {
    status.value = error?.response?.status === 404 ? 'not-found' : 'error'
  }
}

onMounted(load)
</script>

<template>
  <section aria-labelledby="request-title">
    <RouterLink class="request-detail__back" :to="{ name: 'request-list' }">{{ t('requests.detail.back') }}</RouterLink>

    <p v-if="status === 'loading'" role="status">{{ t('requests.detail.loading') }}</p>

    <template v-else-if="status === 'not-found'">
      <h1 id="request-title">{{ t('requests.detail.notFoundTitle') }}</h1>
      <p>{{ t('requests.detail.notFoundText') }}</p>
    </template>

    <div v-else-if="status === 'error'" role="alert">
      <h1 id="request-title">{{ t('requests.detail.errorTitle') }}</h1>
      <p>{{ t('requests.detail.errorText') }}</p>
      <button type="button" class="link-button" @click="load">{{ t('common.retry') }}</button>
    </div>

    <template v-else>
      <div v-if="justCreated" class="request-detail__success" role="status">
        <p class="request-detail__success-title">{{ t('requests.detail.createdTitle') }}</p>
        <p>{{ t('requests.detail.createdText', { phone: request.contact_phone }) }}</p>
      </div>

      <div class="request-detail__head">
        <h1 id="request-title">{{ request.service_detail.name }}</h1>
        <StatusBadge :status="request.status" />
      </div>
      <p class="request-detail__meta">{{ t('requests.detail.number', { id: request.id }) }}</p>

      <div class="surface-card request-detail__card">
        <h2>{{ t('requests.detail.whereTitle') }}</h2>
        <StatusTimeline :status="request.status" />
      </div>

      <div class="surface-card request-detail__card">
        <h2>{{ t('requests.detail.infoTitle') }}</h2>
        <dl class="request-detail__list">
          <div v-for="[label, value] in rows" :key="label" class="request-detail__row">
            <dt>{{ label }}</dt>
            <dd>{{ value }}</dd>
          </div>
        </dl>
      </div>
    </template>
  </section>
</template>

<style scoped>
.request-detail__back {
  display: inline-block;
  margin-bottom: var(--space-4);
  font-weight: 700;
}

.request-detail__success {
  margin-bottom: var(--space-5);
  padding: var(--space-5);
  border-left: 6px solid var(--color-primary);
  border-radius: var(--radius-control);
  background: var(--color-primary-tint);
}

.request-detail__success p {
  margin: 0;
}

.request-detail__success .request-detail__success-title {
  margin-bottom: var(--space-2);
  font-size: var(--text-xl);
  font-weight: 800;
}

.request-detail__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
}

.request-detail__head h1 {
  margin: 0;
}

.request-detail__meta {
  margin-top: var(--space-2);
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}

.request-detail__card {
  margin-top: var(--space-5);
}

.request-detail__card h2 {
  font-size: var(--text-xl);
}

.request-detail__list {
  margin: 0;
}

.request-detail__row {
  display: grid;
  gap: 0 var(--space-4);
  padding: var(--space-3) 0;
  border-top: 1px solid var(--color-line);
}

.request-detail__row dt {
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}

.request-detail__row dd {
  margin: 0;
  overflow-wrap: anywhere;
}

@media (min-width: 36rem) {
  .request-detail__row {
    grid-template-columns: 10rem 1fr;
  }
}
</style>
