import { MAX_ELDER_AGE, MAX_PREFERRED_DAYS_AHEAD, MIN_ELDER_AGE } from '@/constants/care'
import { t } from '@/i18n'

import { isoDateAfter, toIsoDate } from './dates'

/** Her sihirbaz adımında hangi alanların bulunduğu; sunucu hatası doğru adıma eşlenir. */
export const STEP_FIELDS = [
  ['service'],
  ['elder_full_name', 'elder_age', 'relationship', 'elder_notes'],
  ['preferred_date', 'time_slot', 'district', 'neighborhood', 'address'],
  ['contact_phone', 'alternate_contact_name', 'alternate_contact_phone'],
  ['consent'],
]

/**
 * Telefonun 10-15 rakamdan oluştuğunu ve izin verilmeyen karakter içermediğini kontrol eder.
 *
 * @param {string} value Telefon.
 * @returns {boolean} Geçerliyse true.
 */
export function isValidPhone(value) {
  const trimmed = value.trim()
  const digits = trimmed.replace(/\D/g, '')
  return /^\+?[\d\s()-]+$/.test(trimmed) && digits.length >= 10 && digits.length <= 15
}

/**
 * Verilen sihirbaz adımının alanlarını backend kurallarıyla aynı şekilde doğrular.
 *
 * @param {number} step Adım sırası (0-4).
 * @param {Record<string, any>} form Form verisi.
 * @param {Date} [today] Bugünün tarihi; testler için verilebilir.
 * @returns {Record<string, string>} Alan adından hata mesajına eşleme; geçerliyse boş nesne.
 */
export function validateStep(step, form, today = new Date()) {
  const errors = {}
  const text = (field) => String(form[field] ?? '').trim()

  if (step === 0 && !form.service) {
    errors.service = t('validation.request.service')
  }
  if (step === 1) {
    if (!text('elder_full_name')) errors.elder_full_name = t('validation.request.elderName')
    const age = Number(form.elder_age)
    if (!text('elder_age')) errors.elder_age = t('validation.request.elderAgeRequired')
    else if (!Number.isInteger(age) || age < MIN_ELDER_AGE || age > MAX_ELDER_AGE) {
      errors.elder_age = t('validation.request.elderAgeRange', { min: MIN_ELDER_AGE, max: MAX_ELDER_AGE })
    }
    if (!form.relationship) errors.relationship = t('validation.request.relationship')
  }
  if (step === 2) {
    const date = text('preferred_date')
    if (!date) errors.preferred_date = t('validation.request.dateRequired')
    else if (date < toIsoDate(today)) errors.preferred_date = t('validation.request.datePast')
    else if (date > isoDateAfter(MAX_PREFERRED_DAYS_AHEAD, today)) {
      errors.preferred_date = t('validation.request.dateFar', { days: MAX_PREFERRED_DAYS_AHEAD })
    }
    if (!form.time_slot) errors.time_slot = t('validation.request.timeSlot')
    if (!form.district) errors.district = t('validation.location.district')
    else if (!form.neighborhood) errors.neighborhood = t('validation.location.neighborhood')
    if (!text('address')) errors.address = t('validation.request.address')
  }
  if (step === 3) {
    if (!text('contact_phone')) errors.contact_phone = t('validation.request.phoneRequired')
    else if (!isValidPhone(text('contact_phone'))) errors.contact_phone = t('validation.request.phoneInvalidExample')
    const altName = text('alternate_contact_name')
    const altPhone = text('alternate_contact_phone')
    if (altName && !altPhone) errors.alternate_contact_phone = t('validation.request.alternatePhoneRequired')
    if (altPhone && !altName) errors.alternate_contact_name = t('validation.request.alternateNameRequired')
    if (altPhone && !isValidPhone(altPhone)) errors.alternate_contact_phone = t('validation.request.alternatePhoneInvalid')
  }
  if (step === 4 && !form.consent) {
    errors.consent = t('validation.request.consent')
  }
  return errors
}

/**
 * Sunucu hatası alanlarından hatanın ait olduğu ilk adımı bulur.
 *
 * @param {Record<string, string>} fieldErrors Alan hataları.
 * @returns {number} Adım sırası; eşleşme yoksa son adım.
 */
export function stepOfFields(fieldErrors) {
  const index = STEP_FIELDS.findIndex((fields) => fields.some((field) => field in fieldErrors))
  return index === -1 ? STEP_FIELDS.length - 1 : index
}
