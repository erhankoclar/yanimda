import { defineStore } from 'pinia'
import { computed, reactive, ref, watch } from 'vue'

import { requestsApi } from '@/api/requests'
import { parseApiError } from '@/utils/apiErrors'
import { STEP_FIELDS, stepOfFields, validateStep } from '@/utils/requestValidation'

export const WIZARD_STEPS = ['Hizmet', 'Yakınınız', 'Zaman ve adres', 'İletişim', 'Özet ve onay']
const DRAFT_KEY = 'yanimda.requestDraft'
const ALL_FIELDS = STEP_FIELDS.flat()

/**
 * Boş form verisini döndürür.
 *
 * @returns {Record<string, any>} Form alanları.
 */
function emptyForm() {
  return {
    service: null,
    elder_full_name: '',
    elder_age: '',
    relationship: '',
    elder_notes: '',
    preferred_date: '',
    time_slot: '',
    city: '',
    district: '',
    address: '',
    contact_phone: '',
    alternate_contact_name: '',
    alternate_contact_phone: '',
    consent: false,
  }
}

/**
 * Oturum deposundan taslağı okur; depolama erişilemezse null döner.
 *
 * @returns {{ step: number, form: Record<string, any> } | null} Taslak.
 */
function readDraft() {
  try {
    return JSON.parse(window.sessionStorage.getItem(DRAFT_KEY))
  } catch {
    return null
  }
}

/**
 * Taslağı oturum deposuna yazar ya da null ise siler.
 *
 * @param {{ step: number, form: Record<string, any> } | null} draft Taslak.
 */
function writeDraft(draft) {
  try {
    if (draft) window.sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft))
    else window.sessionStorage.removeItem(DRAFT_KEY)
  } catch {
    // Depolama yoksa taslak yalnızca sayfa açıkken korunur.
  }
}

export const useRequestWizardStore = defineStore('requestWizard', () => {
  const step = ref(0)
  const form = reactive(emptyForm())
  const errors = ref({})
  const generalError = ref('')
  const submitting = ref(false)

  // Son adımda mıyız; gezinme düğmesinin metnini belirler.
  const isLastStep = computed(() => step.value === WIZARD_STEPS.length - 1)

  /**
   * Taslağı geri yükler ve gerekirse başlangıç değerlerini uygular.
   *
   * @param {{ serviceId?: number | null, phone?: string }} [defaults] Bağlantıdan gelen hizmet ve profildeki telefon.
   */
  function start({ serviceId = null, phone = '' } = {}) {
    const draft = readDraft()
    if (draft?.form) {
      Object.assign(form, emptyForm(), draft.form)
      step.value = Math.min(Math.max(draft.step ?? 0, 0), WIZARD_STEPS.length - 1)
    }
    if (serviceId) {
      form.service = serviceId
    }
    if (!form.contact_phone && phone) form.contact_phone = phone
    errors.value = {}
    generalError.value = ''
  }

  /**
   * Geçerli adımı doğrular; hatalıysa hataları yazar.
   *
   * @returns {boolean} Adım geçerliyse true.
   */
  function validateCurrent() {
    errors.value = validateStep(step.value, form)
    return Object.keys(errors.value).length === 0
  }

  /**
   * Geçerliyse bir sonraki adıma geçer.
   *
   * @returns {boolean} Geçiş yapıldıysa true.
   */
  function next() {
    if (!validateCurrent()) return false
    step.value = Math.min(step.value + 1, WIZARD_STEPS.length - 1)
    return true
  }

  /** Bir önceki adıma döner; hataları temizler. */
  function back() {
    errors.value = {}
    step.value = Math.max(step.value - 1, 0)
  }

  /**
   * Daha önce geçilmiş bir adıma (ör. özetten düzenleme) döner.
   *
   * @param {number} target Hedef adım.
   */
  function goTo(target) {
    if (target >= 0 && target < step.value) {
      errors.value = {}
      step.value = target
    }
  }

  /**
   * Başvuruyu gönderir. Sunucu alan hatası verirse hatanın ait olduğu adıma döner.
   *
   * @returns {Promise<object | null>} Oluşturulan başvuru; başarısızsa null.
   */
  async function submit() {
    generalError.value = ''
    if (!validateCurrent()) return null
    submitting.value = true
    try {
      const payload = { ...form, elder_age: Number(form.elder_age) }
      const created = await requestsApi.create(payload)
      reset()
      return created
    } catch (error) {
      const parsed = parseApiError(error, ALL_FIELDS)
      errors.value = parsed.fields
      generalError.value = parsed.general
      if (Object.keys(parsed.fields).length) step.value = stepOfFields(parsed.fields)
      return null
    } finally {
      submitting.value = false
    }
  }

  /** Formu ve taslağı temizler. */
  function reset() {
    Object.assign(form, emptyForm())
    step.value = 0
    errors.value = {}
    generalError.value = ''
    writeDraft(null)
  }

  // Her değişiklik taslağa yazılır; girişe gidip dönen veya sayfayı yenileyen kullanıcı kaldığı yerden devam eder.
  watch([step, form], () => writeDraft({ step: step.value, form: { ...form } }), { deep: true, flush: 'sync' })

  return { step, form, errors, generalError, submitting, isLastStep, start, next, back, goTo, submit, reset }
})
