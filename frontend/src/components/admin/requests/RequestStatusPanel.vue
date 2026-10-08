<script setup>
import Button from 'primevue/button'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import Textarea from 'primevue/textarea'
import { computed, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { statusClass, statusSeverity } from '@/admin/status'
import { statusLabel } from '@/constants/care'

const ADMIN_NOTE_MAX = 2000

const props = defineProps({
  /** Başvuru detayı: `status`, `next_statuses`, `admin_note`. */
  request: { type: Object, required: true },
  /** Sunucudan gelen alan hataları: `status`, `admin_note`. */
  errors: { type: Object, default: () => ({}) },
  saving: { type: Boolean, default: false },
})

const emit = defineEmits({
  /** Kaydet: yalnızca değişen alanlar gönderilir. */
  save: (changes) => typeof changes === 'object',
})

const { t } = useI18n()

const form = reactive({ status: '', admin_note: '' })

// Başvuru (yeniden) yüklenince form sunucudaki değerlerle eşitlenir.
watch(() => props.request, (request) => {
  form.status = ''
  form.admin_note = request.admin_note ?? ''
}, { immediate: true })

const nextOptions = computed(() => props.request.next_statuses.map((value) => ({ value, label: statusLabel(value) })))
const isFinal = computed(() => props.request.next_statuses.length === 0)
const changes = computed(() => {
  const result = {}
  if (form.status) result.status = form.status
  if (form.admin_note !== (props.request.admin_note ?? '')) result.admin_note = form.admin_note
  return result
})
const hasChanges = computed(() => Object.keys(changes.value).length > 0)
</script>

<template>
  <section class="admin-panel status-panel" aria-labelledby="status-panel-title">
    <div class="admin-panel__head">
      <h2 id="status-panel-title">{{ t('admin.requestDetail.statusTitle') }}</h2>
      <Tag :value="statusLabel(request.status)" :severity="statusSeverity(request.status)" :class="statusClass(request.status)" />
    </div>

    <form class="status-panel__form" novalidate @submit.prevent="emit('save', changes)">
      <div class="status-panel__field">
        <label for="status-next">{{ t('admin.requestDetail.nextStatus') }}</label>
        <p v-if="isFinal" class="status-panel__hint">{{ t('admin.requestDetail.finalStatus') }}</p>
        <Select
          v-else
          v-model="form.status"
          inputId="status-next"
          :options="nextOptions"
          optionLabel="label"
          optionValue="value"
          showClear
          :placeholder="t('admin.requestDetail.keepStatus')"
          :invalid="!!errors.status"
          fluid
        />
        <small v-if="errors.status" class="status-panel__error">{{ errors.status }}</small>
      </div>

      <div class="status-panel__field">
        <label for="status-note">{{ t('admin.requestDetail.adminNote') }}</label>
        <p id="status-note-hint" class="status-panel__hint">{{ t('admin.requestDetail.adminNoteHint') }}</p>
        <Textarea
          id="status-note"
          aria-describedby="status-note-hint"
          v-model="form.admin_note"
          rows="4"
          autoResize
          :maxlength="ADMIN_NOTE_MAX"
          :invalid="!!errors.admin_note"
          fluid
        />
        <small v-if="errors.admin_note" class="status-panel__error">{{ errors.admin_note }}</small>
      </div>

      <Button type="submit" :label="t('admin.requestDetail.save')" :loading="saving" :disabled="!hasChanges" icon="pi pi-check" />
    </form>
  </section>
</template>

<style scoped>
.status-panel h2 {
  font-size: 1rem;
}

.status-panel__form {
  display: grid;
  gap: 1rem;
}

.status-panel__field {
  display: grid;
  gap: 0.35rem;
}

.status-panel__field label {
  font-weight: 700;
}

.status-panel__hint {
  margin: 0;
  color: var(--admin-ink-soft);
  font-size: 0.85rem;
}

.status-panel__error {
  color: var(--admin-danger);
}
</style>
