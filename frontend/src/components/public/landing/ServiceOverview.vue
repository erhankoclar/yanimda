<script setup>
import { onMounted } from 'vue'

import { useServices } from '@/composables/useServices'

import ServiceIcon from '../ServiceIcon.vue'

const { services, status, load } = useServices()

onMounted(load)
</script>

<template>
  <section id="hizmetler" class="service-overview" aria-labelledby="services-title">
    <div class="container">
      <div class="section-intro">
        <h2 id="services-title">Neler yapabiliriz?</h2>
        <p>Yakınınızın ihtiyacına en yakın hizmeti seçin; ayrıntıları telefonda birlikte konuşuruz.</p>
      </div>

      <p v-if="status === 'loading' || status === 'idle'" class="service-overview__note" role="status">Hizmetler yükleniyor…</p>
      <div v-else-if="status === 'error'" class="service-overview__note" role="alert">
        <p>Hizmetler şu an yüklenemedi. İnternet bağlantınızı kontrol edip tekrar deneyin.</p>
        <button type="button" class="service-overview__retry" @click="load">Tekrar dene</button>
      </div>
      <ul v-else class="service-overview__list">
        <li v-for="service in services" :key="service.id">
          <RouterLink class="service-overview__item" :to="{ name: 'request-new', query: { service: service.id } }">
            <span class="service-overview__icon"><ServiceIcon :name="service.icon" /></span>
            <span class="service-overview__name">{{ service.name }}</span>
            <span class="service-overview__description">{{ service.description }}</span>
            <span class="service-overview__action">Bu hizmete başvur</span>
          </RouterLink>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.service-overview {
  padding: var(--space-7) 0;
  background: var(--color-mist);
}

.section-intro {
  max-width: 36rem;
  margin-bottom: var(--space-6);
}

.section-intro h2 {
  font-size: clamp(2rem, 5vw, 2.75rem);
}

.section-intro p {
  color: var(--color-ink-soft);
  font-size: var(--text-lg);
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
  gap: var(--space-4);
  margin: 0;
  padding: 0;
  list-style: none;
}

.service-overview__item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  height: 100%;
  padding: var(--space-5);
  border: 1px solid var(--color-line);
  border-radius: 1.5rem;
  background: var(--color-surface);
  color: var(--color-ink);
  text-decoration: none;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}

.service-overview__item:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-soft);
}

.service-overview__icon {
  display: grid;
  place-items: center;
  width: 4rem;
  height: 4rem;
  margin-bottom: var(--space-2);
  border-radius: 1.25rem;
  background: var(--color-primary-tint);
  color: var(--color-primary);
}

.service-overview__name {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  line-height: 1.2;
}

.service-overview__description {
  flex: 1;
  color: var(--color-ink-soft);
}

.service-overview__action {
  margin-top: var(--space-2);
  color: var(--color-primary);
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 0.2em;
}

@media (min-width: 40rem) {
  .service-overview__list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 64rem) {
  .service-overview__list {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
