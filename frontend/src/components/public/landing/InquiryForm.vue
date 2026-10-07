<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { inquiriesApi } from '@/api/inquiries'
import { parseApiError } from '@/utils/apiErrors'
import { INQUIRY_MESSAGE_MAX, validateInquiry } from '@/utils/inquiryValidation'

import BaseCheckbox from '../BaseCheckbox.vue'
import BaseInput from '../BaseInput.vue'
import BaseSelect from '../BaseSelect.vue'
import BaseTextarea from '../BaseTextarea.vue'
import FormAlert from '../FormAlert.vue'
import PrimaryButton from '../PrimaryButton.vue'

const { t } = useI18n()

const FIELDS = ['full_name', 'email', 'service', 'message', 'consent']

const props = defineProps({
  services: { type: Array, required: true },
  /** Hizmet kartından gelindiyse önceden seçilecek hizmet. */
  initialService: { type: Number, default: null },
})

/**
 * Boş form verisini döndürür.
 *
 * @returns {Record<string, any>} Form alanları.
 */
function emptyForm() {
  return { full_name: '', email: '', service: props.initialService ?? '', message: '', consent: false, website: '' }
}

const form = reactive(emptyForm())
const errors = ref({})
const generalError = ref('')
// idle → submitting → success | error
const status = ref('idle')
const saved = ref(null)
const successPanel = ref(null)

// Hizmet seçim kutusunun seçenekleri.
const serviceOptions = computed(() => props.services.map((service) => ({ value: service.id, label: service.name })))
const submitting = computed(() => status.value === 'submitting')

// Hizmet kartına tıklanınca seçim güncellenir.
watch(() => props.initialService, (value) => {
  if (value) form.service = value
})

/** Formu doğrular ve gönderir; başarı yalnızca sunucu kaydı döndürdüğünde gösterilir. */
async function submit() {
  generalError.value = ''
  errors.value = validateInquiry(form)
  if (Object.keys(errors.value).length) {
    status.value = 'error'
    await focusFirstError()
    return
  }
  status.value = 'submitting'
  try {
    const result = await inquiriesApi.create({ ...form, service: Number(form.service) })
    if (!result?.id) throw new Error('Sunucu kayıt numarası döndürmedi.')
    saved.value = result
    status.value = 'success'
    await nextTick()
    successPanel.value?.focus()
  } catch (error) {
    const parsed = parseApiError(error, FIELDS)
    errors.value = parsed.fields
    generalError.value = parsed.general
    status.value = 'error'
    await focusFirstError()
  }
}

/** Başarı ekranından yeni ve boş bir forma döner. */
function startOver() {
  Object.assign(form, emptyForm())
  errors.value = {}
  generalError.value = ''
  saved.value = null
  status.value = 'idle'
}

/** İlk hatalı alana odaklanır. */
async function focusFirstError() {
  await nextTick()
  document.querySelector('#talep-formu [aria-invalid="true"]')?.focus()
}
</script>

<template>
  <section id="talep-formu" class="inquiry" aria-labelledby="inquiry-title">
    <div class="container inquiry__grid">
      <div class="inquiry__intro">
        <h2 id="inquiry-title">{{ t('landing.inquiry.title') }}</h2>
        <p>{{ t('landing.inquiry.intro') }}</p>
        <p class="inquiry__alt">
          {{ t('landing.inquiry.altBefore') }}
          <RouterLink :to="{ name: 'request-new' }">{{ t('landing.inquiry.altLink') }}</RouterLink>.
        </p>
      </div>

      <div class="inquiry__card surface-card">
        <div v-if="status === 'success'" ref="successPanel" class="inquiry__success" role="status" tabindex="-1">
          <p class="inquiry__success-title">{{ t('landing.inquiry.successTitle') }}</p>
          <i18n-t keypath="landing.inquiry.successBody" tag="p">
            <template #id><strong>#{{ saved.id }}</strong></template>
            <template #email>{{ form.email }}</template>
          </i18n-t>
          <PrimaryButton variant="secondary" @click="startOver">{{ t('landing.inquiry.startOver') }}</PrimaryButton>
        </div>

        <form v-else novalidate :aria-busy="submitting ? 'true' : 'false'" @submit.prevent="submit">
          <FormAlert :message="generalError" />
          <fieldset class="wizard-fieldset" :disabled="submitting">
            <legend class="visually-hidden">{{ t('landing.inquiry.legend') }}</legend>
            <BaseInput v-model="form.full_name" :label="t('landing.inquiry.fullName')" autocomplete="name" required :error="errors.full_name" />
            <BaseInput
              v-model="form.email"
              :label="t('landing.inquiry.email')"
              type="email"
              inputmode="email"
              autocomplete="email"
              required
              :error="errors.email"
            />
            <BaseSelect
              v-model="form.service"
              :label="t('landing.inquiry.service')"
              :options="serviceOptions"
              :placeholder="t('landing.inquiry.servicePlaceholder')"
              required
              :error="errors.service"
            />
            <BaseTextarea
              v-model="form.message"
              :label="t('landing.inquiry.message')"
              :hint="t('landing.inquiry.messageHint')"
              :maxlength="INQUIRY_MESSAGE_MAX"
              required
              :error="errors.message"
            />
            <!-- Spam tuzağı: insanlara görünmez, yalnızca botlar doldurur. -->
            <div class="inquiry__trap" aria-hidden="true">
              <label for="inquiry-website">{{ t('landing.inquiry.website') }}</label>
              <input id="inquiry-website" v-model="form.website" type="text" name="website" tabindex="-1" autocomplete="off" />
            </div>
            <BaseCheckbox v-model="form.consent" required :error="errors.consent">
              {{ t('landing.inquiry.consent') }}
            </BaseCheckbox>
          </fieldset>
          <PrimaryButton type="submit" block :loading="submitting">
            {{ submitting ? t('landing.inquiry.submitting') : t('landing.inquiry.submit') }}
          </PrimaryButton>
          <p class="visually-hidden" role="status" aria-live="polite">{{ submitting ? t('landing.inquiry.sending') : '' }}</p>
        </form>
      </div>
    </div>
  </section>
</template>

<style scoped>
.inquiry {
  padding: var(--space-7) 0;
  background: var(--color-mist);
}

.inquiry__grid {
  display: grid;
  gap: var(--space-6);
  align-items: start;
}

.inquiry h2 {
  font-size: clamp(2rem, 5vw, 2.75rem);
}

.inquiry__intro p {
  color: var(--color-ink-soft);
  font-size: var(--text-lg);
}

.inquiry__intro .inquiry__alt {
  font-size: var(--text-base);
}

.inquiry__trap {
  position: absolute;
  left: -10000px;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

.inquiry__success:focus {
  outline: none;
}

.inquiry__success-title {
  margin-bottom: var(--space-2);
  padding-left: 3rem;
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='12' fill='%231f5f55'/%3E%3Cpath d='m7 12.5 3.2 3.2L17 8.8' fill='none' stroke='%23fff' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")
    left center / 2.25rem no-repeat;
  min-height: 2.25rem;
  display: flex;
  align-items: center;
}

@media (min-width: 60rem) {
  .inquiry__grid {
    grid-template-columns: 1fr 1.2fr;
    gap: var(--space-7);
  }
}
</style>
