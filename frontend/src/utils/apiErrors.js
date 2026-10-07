import { t } from '@/i18n'

/**
 * API hatasını form alanlarına ve genel bir mesaja ayırır.
 *
 * DRF alan hataları (`{ email: ['...'] }`) ilgili alana, `detail` ve
 * `non_field_errors` genel mesaja yazılır. Ağ ve hız sınırı hataları için
 * kullanıcıya ne yapacağını söyleyen sabit mesajlar kullanılır.
 *
 * @param {any} error axios hatası.
 * @param {string[]} fieldNames Formda gösterilen alan adları; bunların dışındaki alan hataları genel mesaja eklenir.
 * @returns {{ fields: Record<string, string>, general: string }} Alan hataları ve genel mesaj.
 */
export function parseApiError(error, fieldNames = []) {
  const response = error?.response
  if (!response) {
    return { fields: {}, general: t('errors.network') }
  }
  if (response.status === 429) {
    return { fields: {}, general: t('errors.tooMany') }
  }
  if (response.status >= 500) {
    return { fields: {}, general: t('errors.server') }
  }

  const data = response.data ?? {}
  const fields = {}
  const general = []
  Object.entries(typeof data === 'object' ? data : {}).forEach(([key, value]) => {
    const message = Array.isArray(value) ? value.join(' ') : String(value)
    if (fieldNames.includes(key)) fields[key] = message
    else general.push(message)
  })
  if (!general.length && !Object.keys(fields).length) {
    general.push(t('errors.generic'))
  }
  return { fields, general: general.join(' ') }
}
