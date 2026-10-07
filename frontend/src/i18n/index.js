import { createI18n } from 'vue-i18n'

import en from './locales/en'
import tr from './locales/tr'

export const SUPPORTED_LOCALES = ['tr', 'en']
export const DEFAULT_LOCALE = 'tr'

/**
 * Uygulamanın i18n örneği. Bileşenler `useI18n()`, bileşen dışı kod (doğrulama,
 * hata metinleri) `i18n.global.t` kullanır.
 */
export const i18n = createI18n({
  legacy: false,
  locale: DEFAULT_LOCALE,
  fallbackLocale: DEFAULT_LOCALE,
  messages: { tr, en },
})

/**
 * Bileşen dışından çeviri yapar.
 *
 * @param {string} key Mesaj anahtarı.
 * @param {Record<string, any>} [params] Yer tutucu değerleri.
 * @returns {string} Etkin dildeki metin.
 */
export const t = (key, params) => i18n.global.t(key, params)

/**
 * Etkin dili döndürür (`tr` veya `en`).
 *
 * @returns {string} Dil kodu.
 */
export const currentLocale = () => i18n.global.locale.value
