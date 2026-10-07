export const INQUIRY_MESSAGE_MIN = 10
export const INQUIRY_MESSAGE_MAX = 2000

// Tarayıcı tarafında yeterli, sunucunun EmailField kuralıyla uyumlu basit e-posta denetimi.
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

/**
 * Hızlı talep formunu sunucu kurallarıyla aynı şekilde doğrular.
 *
 * @param {{ full_name: string, email: string, service: number | null | '', message: string, consent: boolean }} form Form verisi.
 * @returns {Record<string, string>} Alan adından hata mesajına eşleme; geçerliyse boş nesne.
 */
export function validateInquiry(form) {
  const errors = {}
  const name = form.full_name.trim().replace(/\s+/g, ' ')
  const message = form.message.trim()

  if (name.length < 2) errors.full_name = 'Adınızı ve soyadınızı yazın.'
  if (!form.email.trim()) errors.email = 'E-posta adresinizi yazın.'
  else if (!EMAIL_PATTERN.test(form.email.trim())) errors.email = 'Geçerli bir e-posta adresi yazın. Örnek: ad@ornek.com'
  if (!form.service) errors.service = 'Bir hizmet seçin.'
  if (message.length < INQUIRY_MESSAGE_MIN) {
    errors.message = `İhtiyacınızı en az ${INQUIRY_MESSAGE_MIN} karakterle anlatın.`
  } else if (message.length > INQUIRY_MESSAGE_MAX) {
    errors.message = `Açıklama en fazla ${INQUIRY_MESSAGE_MAX} karakter olabilir.`
  }
  if (!form.consent) errors.consent = 'Talebinizi gönderebilmemiz için bu onayı vermeniz gerekiyor.'
  return errors
}
