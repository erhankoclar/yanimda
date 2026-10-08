import { t } from '@/i18n'

export const INQUIRY_MESSAGE_MIN = 10
export const INQUIRY_MESSAGE_MAX = 2000

// Tarayıcı tarafında yeterli, sunucunun EmailField kuralıyla uyumlu basit e-posta denetimi.
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

/**
 * Hızlı talep formunu sunucu kurallarıyla aynı şekilde doğrular.
 *
 * @param {{ full_name: string, email: string, service: number | null | '', district: number | '', neighborhood: number | '', message: string, consent: boolean }} form Form verisi.
 * @returns {Record<string, string>} Alan adından hata mesajına eşleme; geçerliyse boş nesne.
 */
export function validateInquiry(form) {
  const errors = {}
  const name = form.full_name.trim().replace(/\s+/g, ' ')
  const message = form.message.trim()

  if (name.length < 2) errors.full_name = t('validation.inquiry.fullName')
  if (!form.email.trim()) errors.email = t('validation.emailRequired')
  else if (!EMAIL_PATTERN.test(form.email.trim())) errors.email = t('validation.inquiry.emailInvalid')
  if (!form.service) errors.service = t('validation.inquiry.service')
  if (!form.district) errors.district = t('validation.location.district')
  else if (!form.neighborhood) errors.neighborhood = t('validation.location.neighborhood')
  if (message.length < INQUIRY_MESSAGE_MIN) {
    errors.message = t('validation.inquiry.messageMin', { min: INQUIRY_MESSAGE_MIN })
  } else if (message.length > INQUIRY_MESSAGE_MAX) {
    errors.message = t('validation.inquiry.messageMax', { max: INQUIRY_MESSAGE_MAX })
  }
  if (!form.consent) errors.consent = t('validation.inquiry.consent')
  return errors
}
