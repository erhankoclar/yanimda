<script setup>
import { onMounted, ref } from 'vue'

import { requestsApi } from '@/api/requests'
import RequestListItem from '@/components/public/requests/RequestListItem.vue'
import PrimaryButton from '@/components/public/PrimaryButton.vue'

const requests = ref([])
const status = ref('loading')
const page = ref(1)
const hasMore = ref(false)
const loadingMore = ref(false)

/**
 * Başvuruların istenen sayfasını yükler ve listeye ekler.
 *
 * @param {number} target Sayfa numarası.
 */
async function load(target) {
  const data = await requestsApi.list(target)
  requests.value = target === 1 ? data.results : [...requests.value, ...data.results]
  hasMore.value = Boolean(data.next)
  page.value = target
}

/** İlk sayfayı yükler; hata olursa tekrar denenebilir durum gösterir. */
async function loadFirst() {
  status.value = 'loading'
  try {
    await load(1)
    status.value = 'ready'
  } catch {
    status.value = 'error'
  }
}

/** Sonraki sayfayı listeye ekler. */
async function loadMore() {
  loadingMore.value = true
  try {
    await load(page.value + 1)
  } finally {
    loadingMore.value = false
  }
}

onMounted(loadFirst)
</script>

<template>
  <section aria-labelledby="requests-title">
    <div class="requests__head">
      <h1 id="requests-title">Başvurularım</h1>
      <RouterLink class="requests__new" :to="{ name: 'request-new' }">Yeni başvuru</RouterLink>
    </div>

    <p v-if="status === 'loading'" role="status">Başvurularınız yükleniyor…</p>
    <div v-else-if="status === 'error'" role="alert">
      <p>Başvurularınız şu an yüklenemedi. İnternet bağlantınızı kontrol edip tekrar deneyin.</p>
      <button type="button" class="link-button" @click="loadFirst">Tekrar dene</button>
    </div>
    <div v-else-if="!requests.length" class="requests__empty">
      <h2>Henüz bir başvurunuz yok</h2>
      <p>Yakınınızın neye ihtiyacı olduğunu birkaç adımda anlatın; ekibimiz sizi arasın.</p>
      <RouterLink class="requests__cta" :to="{ name: 'request-new' }">Başvuruya başla</RouterLink>
    </div>
    <template v-else>
      <ul class="requests__list">
        <li v-for="request in requests" :key="request.id">
          <RequestListItem :request="request" />
        </li>
      </ul>
      <PrimaryButton v-if="hasMore" variant="secondary" block :loading="loadingMore" @click="loadMore">
        Daha fazla göster
      </PrimaryButton>
    </template>
  </section>
</template>

<style scoped>
.requests__head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-3);
}

.requests__new {
  font-weight: 700;
}

.requests__list {
  display: grid;
  gap: var(--space-3);
  margin: var(--space-4) 0 var(--space-5);
  padding: 0;
  list-style: none;
}

.requests__empty {
  margin-top: var(--space-5);
  padding: var(--space-6) var(--space-5);
  border-radius: var(--radius-card);
  background: var(--color-primary-tint);
}

.requests__cta {
  display: inline-flex;
  align-items: center;
  min-height: var(--tap-size);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-control);
  background: var(--color-primary);
  color: #fff;
  font-weight: 700;
  text-decoration: none;
}
</style>
