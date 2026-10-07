/**
 * Giriş sonrası yönlendirme adresinin uygulama içi bir yol olduğunu doğrular.
 *
 * `//evil.com` veya `https://evil.com` gibi dış adreslere açık yönlendirmeyi
 * engellemek için yalnızca tek `/` ile başlayan yollar kabul edilir.
 *
 * @param {unknown} value Sorgu parametresinden gelen değer.
 * @param {string} fallback Değer geçersizse kullanılacak yol.
 * @returns {string} Güvenli yönlendirme yolu.
 */
export function safeRedirect(value, fallback) {
  if (typeof value !== 'string') return fallback
  const isInternalPath = value.startsWith('/') && !value.startsWith('//') && !value.startsWith('/\\')
  return isInternalPath ? value : fallback
}
