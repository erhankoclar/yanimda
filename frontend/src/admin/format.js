import { currentLocale } from '@/i18n'

// Arayüz dilinden Intl yerel ayarına eşleme.
const INTL_LOCALES = { tr: 'tr-TR', en: 'en-GB' }

/**
 * Etkin dilin Intl yerel ayarını döndürür.
 *
 * @returns {string} Ör. `tr-TR`.
 */
export function intlLocale() {
  return INTL_LOCALES[currentLocale()] ?? 'tr-TR'
}

/**
 * Sayıyı etkin dilin binlik ayracıyla yazar.
 *
 * @param {number} value Sayı.
 * @returns {string} Biçimlenmiş sayı (ör. "1.250" / "1,250").
 */
export function formatNumber(value) {
  return new Intl.NumberFormat(intlLocale()).format(value ?? 0)
}

/**
 * Geçen aya göre değişim yüzdesini yön ve metin olarak hazırlar.
 *
 * @param {number | null} percent Yuvarlanmış değişim yüzdesi; önceki dönem 0 ise null.
 * @returns {{ trend: 'up' | 'down' | 'flat' | 'none', text: string }} Yön ve işaretsiz yüzde metni
 *   (ör. "%12" / "12%"); kıyas yapılamıyorsa `none` ve boş metin.
 */
export function changeInfo(percent) {
  if (percent === null || percent === undefined) return { trend: 'none', text: '' }
  const trend = percent > 0 ? 'up' : percent < 0 ? 'down' : 'flat'
  const text = new Intl.NumberFormat(intlLocale(), { style: 'percent', maximumFractionDigits: 0 }).format(Math.abs(percent) / 100)
  return { trend, text }
}

/**
 * `YYYY-MM-DD` tarihini kısa gün-ay biçiminde yazar (ör. "6 Eki" / "6 Oct").
 *
 * @param {string} iso Tarih.
 * @returns {string} Kısa tarih.
 */
export function formatShortDate(iso) {
  const [year, month, day] = iso.split('-').map(Number)
  return new Intl.DateTimeFormat(intlLocale(), { day: 'numeric', month: 'short' }).format(new Date(year, month - 1, day))
}

// Göreli zaman için eşikler: bir dakikadan az "şimdi", sonra dakika, saat, gün.
const RELATIVE_STEPS = [
  { unit: 'minute', seconds: 60, limit: 60 },
  { unit: 'hour', seconds: 3600, limit: 24 },
  { unit: 'day', seconds: 86400, limit: Infinity },
]

/**
 * Zamanı şimdiye göre göreli yazar (ör. "12 dakika önce" / "12 minutes ago").
 *
 * @param {string} iso ISO tarih-saat.
 * @param {Date} [now] Karşılaştırma anı; testler için verilebilir.
 * @returns {string} Göreli zaman.
 */
export function formatRelativeTime(iso, now = new Date()) {
  const seconds = Math.max(0, (now.getTime() - new Date(iso).getTime()) / 1000)
  const formatter = new Intl.RelativeTimeFormat(intlLocale(), { numeric: 'auto' })
  if (seconds < 60) return formatter.format(0, 'second')
  for (const step of RELATIVE_STEPS) {
    const value = Math.floor(seconds / step.seconds)
    if (value < step.limit) return formatter.format(-value, step.unit)
  }
  return ''
}

/**
 * ISO tarih-saati kısa tarih ve saat olarak yazar (ör. "8 Eki 2026 14:05").
 *
 * @param {string} iso ISO tarih-saat.
 * @returns {string} Biçimlenmiş metin; boşsa boş.
 */
export function formatDateTime(iso) {
  if (!iso) return ''
  return new Intl.DateTimeFormat(intlLocale(), { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    .format(new Date(iso))
}
