<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { requestsApi } from '@/api/requests'
import StatusBadge from '@/components/public/requests/StatusBadge.vue'
import StatusTimeline from '@/components/public/requests/StatusTimeline.vue'
import { RELATIONSHIP_OPTIONS, TIME_SLOT_OPTIONS, optionLabel } from '@/constants/care'
import { formatLongDate } from '@/utils/dates'

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
    ['Yakınınız', `${item.elder_full_name}, ${item.elder_age} yaşında`],
    ['Yakınlığınız', optionLabel(RELATIONSHIP_OPTIONS, item.relationship)],
    ['Tarih', `${formatLongDate(item.preferred_date)}, ${optionLabel(TIME_SLOT_OPTIONS, item.time_slot)}`],
    ['Adres', `${item.address}, ${item.district} / ${item.city}`],
    ['Telefonunuz', item.contact_phone],
    ['İkinci kişi', item.alternate_contact_name ? `${item.alternate_contact_name}, ${item.alternate_contact_phone}` : 'Yok'],
    ['Notlar', item.elder_notes || 'Yok'],
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
    <RouterLink class="request-detail__back" :to="{ name: 'request-list' }">Başvurularıma dön</RouterLink>

    <p v-if="status === 'loading'" role="status">Başvuru yükleniyor…</p>

    <template v-else-if="status === 'not-found'">
      <h1 id="request-title">Bu başvuru bulunamadı</h1>
      <p>Bağlantı hatalı olabilir ya da bu başvuru size ait değil.</p>
    </template>

    <div v-else-if="status === 'error'" role="alert">
      <h1 id="request-title">Başvuru yüklenemedi</h1>
      <p>İnternet bağlantınızı kontrol edip tekrar deneyin.</p>
      <button type="button" class="link-button" @click="load">Tekrar dene</button>
    </div>

    <template v-else>
      <div v-if="justCreated" class="request-detail__success" role="status">
        <p class="request-detail__success-title">Başvurunuz alındı</p>
        <p>Teşekkür ederiz. Ekibimiz başvurunuzu inceleyip {{ request.contact_phone }} numarasından sizi arayacak.</p>
      </div>

      <div class="request-detail__head">
        <h1 id="request-title">{{ request.service_detail.name }}</h1>
        <StatusBadge :status="request.status" />
      </div>
      <p class="request-detail__meta">Başvuru no: {{ request.id }}</p>

      <h2>Başvurunuz nerede?</h2>
      <StatusTimeline :status="request.status" />

      <h2>Başvuru bilgileri</h2>
      <dl class="request-detail__list">
        <div v-for="[label, value] in rows" :key="label" class="request-detail__row">
          <dt>{{ label }}</dt>
          <dd>{{ value }}</dd>
        </div>
      </dl>
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
