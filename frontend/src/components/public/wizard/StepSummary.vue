<script setup>
import { computed } from 'vue'

import BaseCheckbox from '../BaseCheckbox.vue'

import { RELATIONSHIP_OPTIONS, TIME_SLOT_OPTIONS, optionLabel } from '@/constants/care'
import { formatLongDate } from '@/utils/dates'

const props = defineProps({
  form: { type: Object, required: true },
  errors: { type: Object, required: true },
  /** Seçilen hizmetin adı. */
  serviceName: { type: String, default: '' },
})

const emit = defineEmits({
  /** Kullanıcı bir bölümü düzenlemek istediğinde ilgili adımın sırası. */
  edit: (step) => Number.isInteger(step),
})

// Özet bölümleri; her biri düzenlenecek adıma bağlıdır.
const sections = computed(() => [
  { step: 0, title: 'Hizmet', rows: [['Seçilen hizmet', props.serviceName]] },
  {
    step: 1,
    title: 'Yakınınız',
    rows: [
      ['Adı ve soyadı', props.form.elder_full_name],
      ['Yaşı', props.form.elder_age],
      ['Yakınlığınız', optionLabel(RELATIONSHIP_OPTIONS, props.form.relationship)],
      ['Notlar', props.form.elder_notes || 'Yok'],
    ],
  },
  {
    step: 2,
    title: 'Zaman ve adres',
    rows: [
      ['Tarih', formatLongDate(props.form.preferred_date)],
      ['Saat', optionLabel(TIME_SLOT_OPTIONS, props.form.time_slot)],
      ['Adres', `${props.form.address}, ${props.form.district} / ${props.form.city}`],
    ],
  },
  {
    step: 3,
    title: 'İletişim',
    rows: [
      ['Telefonunuz', props.form.contact_phone],
      ['İkinci kişi', props.form.alternate_contact_name
        ? `${props.form.alternate_contact_name}, ${props.form.alternate_contact_phone}`
        : 'Yok'],
    ],
  },
])
</script>

<template>
  <div>
    <p>Göndermeden önce bilgileri kontrol edin. Değiştirmek istediğiniz bölümde “Düzenle”ye basın.</p>
    <section v-for="section in sections" :key="section.step" class="summary-section">
      <div class="summary-section__head">
        <h2>{{ section.title }}</h2>
        <button type="button" class="link-button" @click="emit('edit', section.step)">
          Düzenle<span class="visually-hidden">: {{ section.title }}</span>
        </button>
      </div>
      <dl>
        <div v-for="[label, value] in section.rows" :key="label" class="summary-section__row">
          <dt>{{ label }}</dt>
          <dd>{{ value }}</dd>
        </div>
      </dl>
    </section>
    <BaseCheckbox v-model="form.consent" required :error="errors.consent">
      Yazdığım bilgilerin hizmeti planlamak için işlenmesini ve ekibin beni aramasını kabul ediyorum.
    </BaseCheckbox>
  </div>
</template>

<style scoped>
.summary-section {
  margin-bottom: var(--space-5);
  padding: var(--space-4) var(--space-5);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-card);
  background: var(--color-surface);
}

.summary-section__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-4);
}

.summary-section__head h2 {
  margin: 0;
  font-size: var(--text-lg);
}

.summary-section dl {
  margin: var(--space-3) 0 0;
}

.summary-section__row {
  display: grid;
  gap: 0 var(--space-4);
  padding: var(--space-2) 0;
  border-top: 1px solid var(--color-line);
}

.summary-section__row dt {
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}

.summary-section__row dd {
  margin: 0;
  overflow-wrap: anywhere;
}

@media (min-width: 36rem) {
  .summary-section__row {
    grid-template-columns: 10rem 1fr;
  }
}
</style>
