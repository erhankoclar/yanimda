import { t } from '@/i18n'

// Backend'deki CareRequest seçenekleriyle aynı değerler; etiketler çeviri anahtarı olarak tutulur
// ve gösterim anında çözülür, böylece dil değişince güncellenir.

export const RELATIONSHIP_OPTIONS = [
  { value: 'parent', labelKey: 'care.relationship.parent' },
  { value: 'grandparent', labelKey: 'care.relationship.grandparent' },
  { value: 'relative', labelKey: 'care.relationship.relative' },
  { value: 'neighbor', labelKey: 'care.relationship.neighbor' },
  { value: 'self', labelKey: 'care.relationship.self' },
]

export const TIME_SLOT_OPTIONS = [
  { value: 'morning', labelKey: 'care.timeSlot.morning' },
  { value: 'afternoon', labelKey: 'care.timeSlot.afternoon' },
  { value: 'evening', labelKey: 'care.timeSlot.evening' },
]

export const STATUS_VALUES = ['new', 'reviewing', 'assigned', 'completed', 'cancelled']

export const MIN_ELDER_AGE = 40
export const MAX_ELDER_AGE = 120
export const MAX_PREFERRED_DAYS_AHEAD = 90

/**
 * Seçenek listesinde değerin etiketini etkin dilde bulur.
 *
 * @param {Array<{ value: string, labelKey: string }>} options Seçenekler.
 * @param {string} value Değer.
 * @returns {string} Çevrilmiş etiket; bulunamazsa değerin kendisi.
 */
export function optionLabel(options, value) {
  const option = options.find((item) => item.value === value)
  return option ? t(option.labelKey) : value
}

/**
 * Seçenekleri `{ value, label }` biçimine çevirir; select bileşenleri bunu bekler.
 * Computed içinde çağrıldığında dil değişince yeniden hesaplanır.
 *
 * @param {Array<{ value: string, labelKey: string }>} options Seçenekler.
 * @returns {Array<{ value: string, label: string }>} Çevrilmiş seçenekler.
 */
export function localizedOptions(options) {
  return options.map((option) => ({ value: option.value, label: t(option.labelKey) }))
}

/**
 * Başvuru durumunun etkin dildeki etiketini döndürür.
 *
 * @param {string} value Durum değeri.
 * @returns {string} Etiket; bilinmeyen durumda değerin kendisi.
 */
export function statusLabel(value) {
  return STATUS_VALUES.includes(value) ? t(`care.status.${value}`) : value
}
