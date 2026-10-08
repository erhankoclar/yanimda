<script setup>
import Skeleton from 'primevue/skeleton'
import { useI18n } from 'vue-i18n'

import { formatRelativeTime } from '@/admin/format'
import ServiceIcon from '@/components/public/ServiceIcon.vue'

defineProps({
  /** Dashboard yanıtındaki `recent`; ilk yüklemede null. */
  items: { type: Array, default: null },
})

const { t, locale } = useI18n()

/**
 * Kaydın açılacağı admin sayfasını döndürür.
 *
 * @param {{ type: 'inquiry' | 'request', id: number }} item Son kayıt.
 * @returns {import('vue-router').RouteLocationRaw} Hedef sayfa.
 */
function targetOf(item) {
  return item.type === 'request'
    ? { name: 'admin-request-detail', params: { id: item.id } }
    : { name: 'admin-inquiries', query: { id: item.id } }
}
</script>

<template>
  <section class="admin-panel recent" aria-labelledby="recent-title">
    <div class="admin-panel__head">
      <h2 id="recent-title">{{ t('admin.dashboard.recent.title') }}</h2>
    </div>

    <ul v-if="!items" class="recent__list" aria-hidden="true">
      <li v-for="index in 5" :key="index" class="recent__skeleton">
        <Skeleton shape="circle" size="2.25rem" />
        <Skeleton width="70%" height="1rem" />
      </li>
    </ul>
    <p v-else-if="!items.length" class="recent__empty">{{ t('admin.dashboard.recent.empty') }}</p>
    <ul v-else class="recent__list">
      <li v-for="item in items" :key="`${item.type}-${item.id}`">
        <RouterLink :to="targetOf(item)" class="recent__item" :data-recent="`${item.type}-${item.id}`">
          <span class="recent__icon"><ServiceIcon :name="item.service.icon" /></span>
          <span class="recent__text">
            <span class="recent__title">{{ item.title }}</span>
            <span class="recent__service">{{ item.service.name }}</span>
            <span class="recent__meta">
              <span class="recent__type" :class="`recent__type--${item.type}`">{{ t(`admin.dashboard.recent.types.${item.type}`) }}</span>
              <time :datetime="item.created_at" :data-locale="locale">{{ formatRelativeTime(item.created_at) }}</time>
            </span>
          </span>
        </RouterLink>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.recent {
  min-width: 0;
}

.recent__list {
  display: grid;
  gap: 0.15rem;
  margin: 0 -0.5rem;
  padding: 0;
  list-style: none;
}

.recent__item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: start;
  gap: 0.7rem;
  padding: 0.55rem 0.5rem;
  border-radius: 0.6rem;
  color: inherit;
  text-decoration: none;
}

.recent__item:hover {
  background: var(--admin-bg);
}

.recent__item:focus-visible {
  outline: 2px solid var(--admin-primary);
  outline-offset: 1px;
}

.recent__icon {
  display: inline-grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: var(--admin-primary-tint);
  color: var(--admin-primary);
}

.recent__icon :deep(.service-icon) {
  width: 1.3rem;
  height: 1.3rem;
}

.recent__text {
  display: grid;
  min-width: 0;
}

.recent__title,
.recent__service {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent__title {
  font-weight: 700;
}

.recent__service {
  color: var(--admin-ink-soft);
  font-size: 0.85rem;
}

.recent__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0 0.5rem;
  color: var(--admin-ink-soft);
  font-size: 0.78rem;
}

.recent__type {
  font-weight: 700;
}

.recent__type--request {
  color: var(--admin-primary);
}

.recent__type--inquiry {
  color: var(--admin-accent-ink);
}

.recent__skeleton {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.55rem 0.5rem;
}

.recent__empty {
  margin: 0;
  color: var(--admin-ink-soft);
}
</style>
