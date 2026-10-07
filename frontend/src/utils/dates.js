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
 * ISO tarihi Türkçe uzun biçimde gösterir (ör. "12 Ekim 2026 Pazartesi").
 *
 * @param {string} iso `YYYY-MM-DD` tarih.
 * @returns {string} Okunabilir tarih.
 */
export function formatLongDate(iso) {
  if (!iso) return ''
  const [year, month, day] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'long', year: 'numeric', weekday: 'long' })
    .format(new Date(year, month - 1, day))
}
