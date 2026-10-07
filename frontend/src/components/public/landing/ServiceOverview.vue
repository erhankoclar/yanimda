<script setup>
import { onMounted, ref } from 'vue'

import { requestsApi } from '@/api/requests'

import ServiceIcon from '../ServiceIcon.vue'

const services = ref([])
const status = ref('loading')

/** Hizmetleri yükler; hata olursa tekrar denenebilir durum gösterilir. */
async function load() {
  status.value = 'loading'
  try {
    services.value = await requestsApi.services()
    status.value = 'ready'
  } catch {
    status.value = 'error'
  }
}

onMounted(load)
</script>

<template>
  <section class="service-overview" aria-labelledby="services-title">
    <h2 id="services-title">Neler yapabiliriz?</h2>
    <p v-if="status === 'loading'" class="service-overview__note" role="status">Hizmetler yükleniyor…</p>
    <div v-else-if="status === 'error'" class="service-overview__note" role="alert">
      <p>Hizmetler şu an yüklenemedi. İnternet bağlantınızı kontrol edip tekrar deneyin.</p>
      <button type="button" class="service-overview__retry" @click="load">Tekrar dene</button>
    </div>
    <ul v-else class="service-overview__list">
      <li v-for="service in services" :key="service.id">
        <RouterLink class="service-overview__item" :to="{ name: 'request-new', query: { service: service.id } }">
          <span class="service-overview__icon"><ServiceIcon :name="service.icon" /></span>
          <span>
            <span class="service-overview__name">{{ service.name }}</span>
            <span class="service-overview__description">{{ service.description }}</span>
          </span>
        </RouterLink>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.service-overview {
  margin-top: var(--space-7);
}

.service-overview__note {
  color: var(--color-ink-soft);
}

.service-overview__retry {
  min-height: 2.75rem;
  padding: 0 var(--space-4);
  border: 2px solid var(--color-line);
  border-radius: var(--radius-control);
  background: var(--color-surface);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.service-overview__list {
  display: grid;
  gap: var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
}

.service-overview__item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-line);
  color: var(--color-ink);
  text-decoration: none;
}

.service-overview__item:hover .service-overview__name {
  text-decoration: underline;
  text-underline-offset: 0.2em;
}

.service-overview__icon {
  display: grid;
  place-items: center;
  flex: none;
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  background: var(--color-primary-tint);
  color: var(--color-primary-dark);
}

.service-overview__icon :deep(svg) {
  width: 2.25rem;
  height: 2.25rem;
}

.service-overview__name {
  display: block;
  font-weight: 800;
}

.service-overview__description {
  display: block;
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}
</style>
