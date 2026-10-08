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
