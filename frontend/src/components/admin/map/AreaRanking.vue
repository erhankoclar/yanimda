<script setup>
import SelectButton from 'primevue/selectbutton'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { formatNumber } from '@/admin/format'
import { ranked } from '@/admin/map/thematic'

const props = defineProps({
  districts: { type: Array, required: true },
  neighborhoods: { type: Array, required: true },
  serviceId: { type: Number, default: null },
})

/** Listelenen seviye; haritanın yakınlaştırmasını izler ama elle de değiştirilebilir. */
const level = defineModel('level', { type: String, default: 'district' })

const emit = defineEmits({
  /** Bir satıra tıklandı. */
  select: (area) => Boolean(area?.level),
})

const { t } = useI18n()

const levelOptions = computed(() => [
  { value: 'district', label: t('admin.map.levels.district') },
  { value: 'neighborhood', label: t('admin.map.levels.neighborhood') },
])

const rows = computed(() => ranked(level.value === 'neighborhood' ? props.neighborhoods : props.districts, props.serviceId)
  .filter((item) => item.value > 0))
const max = computed(() => rows.value[0]?.value ?? 0)
// Kaydı olmayan ilçeler ayrıca sayılır; "en az" ucunu göstermek için.
const emptyDistricts = computed(() => (level.value === 'district'
  ? ranked(props.districts, props.serviceId).filter((item) => item.value === 0).map((item) => item.name)
  : []))
</script>

<template>
  <section class="admin-panel ranking" aria-labelledby="ranking-title">
    <div class="admin-panel__head">
      <h2 id="ranking-title">{{ t('admin.map.ranking') }}</h2>
      <SelectButton
        v-model="level"
        :options="levelOptions"
        optionLabel="label"
        optionValue="value"
        :allowEmpty="false"
        size="small"
        :ariaLabel="t('admin.map.rankingLevel')"
      />
    </div>

    <p v-if="!rows.length" class="ranking__empty">{{ t('admin.map.rankingEmpty') }}</p>
    <ol v-else class="ranking__list">
      <li v-for="(row, index) in rows" :key="row.id">
        <button type="button" class="ranking__row" :data-area="`${level}-${row.id}`" @click="emit('select', { level, id: row.id, name: row.name, count: row.value })">
          <span class="ranking__rank">{{ index + 1 }}</span>
          <span class="ranking__name">{{ row.name }}</span>
          <span class="ranking__count">{{ formatNumber(row.value) }}</span>
          <span class="ranking__bar" aria-hidden="true"><span :style="{ width: `${(row.value / max) * 100}%` }" /></span>
        </button>
      </li>
    </ol>

    <p v-if="emptyDistricts.length" class="ranking__none">
      <strong>{{ t('admin.map.noDemandDistricts', { count: emptyDistricts.length }) }}</strong>
      {{ emptyDistricts.join(', ') }}
    </p>
  </section>
</template>

<style scoped>
.ranking {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}

.ranking__list {
  display: grid;
  align-content: start;
  gap: 0.15rem;
  margin: 0 -0.5rem;
  padding: 0;
  list-style: none;
}

/* Geniş ekranda panel harita yüksekliğindedir; liste kendi içinde kayar. */
@media (min-width: 75rem) {
  .ranking__list {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
  }
}

.ranking__row {
  display: grid;
  grid-template-columns: 1.6rem minmax(0, 1fr) auto;
  gap: 0.15rem 0.5rem;
  width: 100%;
  padding: 0.45rem 0.5rem;
  border: 0;
  border-radius: 0.5rem;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.ranking__row:hover {
  background: var(--admin-bg);
}

.ranking__row:focus-visible {
  outline: 2px solid var(--admin-primary);
  outline-offset: 1px;
}

.ranking__rank {
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
  font-variant-numeric: tabular-nums;
}

.ranking__name {
  overflow: hidden;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ranking__count {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.ranking__bar {
  grid-column: 2 / 4;
  height: 0.3rem;
  border-radius: 999px;
  background: var(--admin-line);
}

.ranking__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--admin-primary);
}

.ranking__empty,
.ranking__none {
  margin: 0;
  color: var(--admin-ink-soft);
  font-size: 0.85rem;
}

.ranking__none {
  margin-top: 0.75rem;
}
</style>
