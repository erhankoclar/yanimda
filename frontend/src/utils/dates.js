import { currentLocale } from '@/i18n'

// Arayüz dilinden Intl yerel ayarına eşleme.
const INTL_LOCALES = { tr: 'tr-TR', en: 'en-GB' }

/**
 * Tarihi yerel saate göre `YYYY-MM-DD` biçiminde döndürür.
 *
 * @param {Date} date Tarih.
 * @returns {string} ISO tarih metni.
 */
export function toIsoDate(date) {
  const pad = (value) => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

/**
 * Bugünden belirtilen gün sonrasının ISO tarihini döndürür.
 *
 * @param {number} days Eklenecek gün sayısı.
 * @param {Date} [from] Başlangıç tarihi; testler için verilebilir.
 * @returns {string} ISO tarih metni.
 */
export function isoDateAfter(days, from = new Date()) {
  const date = new Date(from)
  date.setDate(date.getDate() + days)
  return toIsoDate(date)
}

/**
 * ISO tarihi etkin dilde uzun biçimde gösterir (ör. "12 Ekim 2026 Pazartesi" / "Monday 12 October 2026").
 *
 * @param {string} iso `YYYY-MM-DD` tarih.
 * @returns {string} Okunabilir tarih.
 */
export function formatLongDate(iso) {
  if (!iso) return ''
  const [year, month, day] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat(INTL_LOCALES[currentLocale()] ?? 'tr-TR', { day: 'numeric', month: 'long', year: 'numeric', weekday: 'long' })
    .format(new Date(year, month - 1, day))
}
