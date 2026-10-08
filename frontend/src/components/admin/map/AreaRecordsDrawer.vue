<script setup>
import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import Message from 'primevue/message'
import SelectButton from 'primevue/selectbutton'
import Skeleton from 'primevue/skeleton'
import Tag from 'primevue/tag'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { formatNumber, formatRelativeTime } from '@/admin/format'
import { statusClass, statusSeverity } from '@/admin/status'
import { adminApi } from '@/api/admin'
import ServiceIcon from '@/components/public/ServiceIcon.vue'
import { statusLabel } from '@/constants/care'
import { parseApiError } from '@/utils/apiErrors'
import { isoDateAfter } from '@/utils/dates'

const visible = defineModel('visible', { type: Boolean, default: false })

const props = defineProps({
  /** Seçilen alan: `{ level, id, name, count }`; il için `id` null'dır. */
  area: { type: Object, default: null },
  source: { type: String, default: 'all' },
  serviceId: { type: Number, default: null },
  days: { type: Number, default: null },
})

const { t } = useI18n()

// Kullanıcının çekmecede seçtiği tür; kaynak tek türe süzülmüşse o tür kullanılır.
const kind = ref('requests')
const activeKind = computed(() => (props.source === 'all' ? kind.value : props.source))
const items = ref([])
const nextPage = ref(null)
const loading = ref(false)
const error = ref('')

const kindOptions = computed(() => [
  { value: 'requests', label: t('admin.map.records.requests') },
  { value: 'inquiries', label: t('admin.map.records.inquiries') },
])

/**
 * Seçili alan ve harita seçimlerinden liste süzgeçlerini kurar; harita sayısıyla aynı kayıtlar gelir.
 *
 * @param {number} page Sayfa.
 * @returns {Record<string, any>} Sorgu parametreleri.
 */
function filters(page) {
  const params = { page }
  if (props.area?.level === 'district') params.district = props.area.id
  if (props.area?.level === 'neighborhood') params.neighborhood = props.area.id
  if (props.serviceId) params.service = props.serviceId
  // Dönem, harita uç noktasıyla aynı şekilde bugünü de içeren son N gündür.
  if (props.days) params.created_from = isoDateAfter(-(props.days - 1))
  return params
}

/**
 * Kayıtları yükler; `append` ile sonraki sayfa listeye eklenir.
 *
 * @param {boolean} [append] Sonraki sayfa mı.
 */
async function load(append = false) {
  if (!props.area) return
  loading.value = true
  error.value = ''
  try {
    const page = append ? nextPage.value : 1
    const fetcher = activeKind.value === 'requests' ? adminApi.requests : adminApi.inquiries
    const result = await fetcher(filters(page))
    items.value = append ? [...items.value, ...result.results] : result.results
    nextPage.value = result.next ? page + 1 : null
  } catch (failure) {
    error.value = parseApiError(failure).general
  } finally {
    loading.value = false
  }
}

// Çekmece açıkken alan, seçimler veya tür değişince liste bir kez yeniden yüklenir;
// açılışta alan ve görünürlük aynı anda değiştiği için tek izleyici kullanılır.
watch(() => [visible.value, props.area, props.serviceId, props.days, activeKind.value], () => {
  if (visible.value) load()
})
</script>

<template>
  <Drawer v-model:visible="visible" position="right" class="admin-shell area-drawer" :pt="{ root: { 'aria-labelledby': 'area-drawer-title' } }">
    <template #header>
      <div class="area-drawer__head">
        <h2 id="area-drawer-title">{{ area?.name }}</h2>
        <p>{{ t('admin.map.records.summary', { count: formatNumber(area?.count ?? 0) }) }}</p>
      </div>
    </template>

    <SelectButton
      v-if="source === 'all'"
      v-model="kind"
      :options="kindOptions"
      optionLabel="label"
      optionValue="value"
      :allowEmpty="false"
      size="small"
      class="area-drawer__kind"
      :ariaLabel="t('admin.map.records.kind')"
    />

    <Message v-if="error" severity="error" :closable="false" role="alert">{{ error }}</Message>

    <div v-if="loading && !items.length" aria-hidden="true">
      <Skeleton v-for="index in 4" :key="index" height="3.2rem" class="area-drawer__skeleton" />
    </div>
    <p v-else-if="!items.length && !error" class="area-drawer__empty">{{ t('admin.map.records.empty') }}</p>
    <ul v-else class="area-drawer__list">
      <li v-for="item in items" :key="item.id">
        <RouterLink
          :to="activeKind === 'requests'
            ? { name: 'admin-request-detail', params: { id: item.id } }
            : { name: 'admin-inquiries', query: { id: item.id } }"
          class="area-drawer__item"
        >
          <span class="area-drawer__icon"><ServiceIcon :name="item.service.icon" /></span>
          <span class="area-drawer__text">
            <span class="area-drawer__title">{{ activeKind === 'requests' ? item.elder_full_name : item.full_name }}</span>
            <span class="area-drawer__meta">
              {{ item.service.name }}<template v-if="item.location">, {{ item.location.neighborhood.name }}</template>
            </span>
            <time :datetime="item.created_at" class="area-drawer__time">{{ formatRelativeTime(item.created_at) }}</time>
          </span>
          <Tag v-if="activeKind === 'requests'" :value="statusLabel(item.status)" :severity="statusSeverity(item.status)" :class="statusClass(item.status)" />
        </RouterLink>
      </li>
    </ul>

    <Button
      v-if="nextPage"
      :label="t('admin.map.records.more')"
      :loading="loading"
      text
      class="area-drawer__more"
      @click="load(true)"
    />
  </Drawer>
</template>

<style>
/* PrimeVue'nun sağ çekmece genişliğini (20rem) ezmek için seçici daha özeldir; dar ekranda tam genişlik olur. */
.p-drawer-right .p-drawer.area-drawer.admin-shell {
  min-height: 0;
  width: min(26rem, 100vw);
}
</style>

<style scoped>
.area-drawer__head h2 {
  font-size: 1.15rem;
}

.area-drawer__head p {
  margin: 0.15rem 0 0;
  color: var(--admin-ink-soft);
  font-size: 0.85rem;
}

.area-drawer__kind {
  margin-bottom: 0.75rem;
}

.area-drawer__list {
  display: grid;
  gap: 0.15rem;
  margin: 0 -0.5rem;
  padding: 0;
  list-style: none;
}

.area-drawer__item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem;
  border-radius: 0.6rem;
  color: inherit;
  text-decoration: none;
}

.area-drawer__item:hover {
  background: var(--admin-bg);
}

.area-drawer__item:focus-visible {
  outline: 2px solid var(--admin-primary);
  outline-offset: 1px;
}

.area-drawer__icon {
  display: inline-grid;
  place-items: center;
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 50%;
  background: var(--admin-primary-tint);
  color: var(--admin-primary);
}

.area-drawer__icon :deep(.service-icon) {
  width: 1.2rem;
  height: 1.2rem;
}

.area-drawer__text {
  display: grid;
  min-width: 0;
}

.area-drawer__title,
.area-drawer__meta {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.area-drawer__title {
  font-weight: 700;
}

.area-drawer__meta,
.area-drawer__time {
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
}

.area-drawer__skeleton {
  margin-bottom: 0.5rem;
}

.area-drawer__empty {
  margin: 0;
  color: var(--admin-ink-soft);
}

.area-drawer__more {
  width: 100%;
  margin-top: 0.5rem;
}
</style>
