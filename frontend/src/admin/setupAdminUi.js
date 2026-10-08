/**
 * Admin arayüzünün PrimeVue kurulumu.
 *
 * PrimeVue yalnızca admin tarafında kullanılır. Bu modül yalnızca admin
 * route'larına ilk girişte dinamik olarak yüklenir; böylece PrimeVue ve tema
 * son kullanıcı sayfalarının paketlerine hiç girmez.
 */
import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'
import PrimeVue, { defaultOptions } from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'

import { watch } from 'vue'

import 'primeicons/primeicons.css'
import '@/styles/admin.css'
import { i18n } from '@/i18n'

import { trLocale } from './trLocale'

// PrimeVue'nun kendi İngilizce metinleri; kurulumdan önce kopyalanır.
const enLocale = { ...defaultOptions.locale }

/**
 * Arayüz diline karşılık gelen PrimeVue metinlerini döndürür.
 *
 * @param {string} locale `tr` veya `en`.
 * @returns {object} PrimeVue locale nesnesi.
 */
export function primeLocaleFor(locale) {
  return locale === 'en' ? enLocale : trLocale
}

// Markanın çam yeşili (#1f5f55) etrafında üretilmiş birincil renk ölçeği.
const YanimdaPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#eef6f4',
      100: '#d5ebe6',
      200: '#acd6cd',
      300: '#7dbbae',
      400: '#4f9b8d',
      500: '#2e7d70',
      600: '#1f5f55',
      700: '#1a4f47',
      800: '#163f39',
      900: '#12322e',
      950: '#0a1e1b',
    },
    // Koyu temada PrimeVue yüzeyleri (çekmece, giriş alanları, paneller) admin.css'teki
    // yeşilimsi koyu tonlarla aynı olsun; 900 = --admin-surface, 950 = --admin-bg.
    colorScheme: {
      dark: {
        surface: {
          0: '#ffffff',
          50: '#eef3f1',
          100: '#d9e3df',
          200: '#b9c8c3',
          300: '#93a7a0',
          400: '#6e857e',
          500: '#52685f',
          600: '#3d514b',
          700: '#2a3b37',
          800: '#21302c',
          900: '#182522',
          950: '#101a18',
        },
      },
    },
  },
})

/**
 * PrimeVue'yu, Toast ve onay servislerini uygulamaya kurar; PrimeVue metinleri arayüz dilini izler.
 *
 * @param {import('vue').App} app Vue uygulaması.
 */
export function setupAdminUi(app) {
  app.use(PrimeVue, {
    theme: { preset: YanimdaPreset, options: { darkModeSelector: "[data-theme='dark']", cssLayer: false } },
    locale: primeLocaleFor(i18n.global.locale.value),
  })
  app.use(ToastService)
  app.use(ConfirmationService)
  // Tarih seçici, tablo ve sayfalama metinleri dil bayrağıyla birlikte değişir.
  watch(i18n.global.locale, (locale) => {
    app.config.globalProperties.$primevue.config.locale = primeLocaleFor(locale)
  })
}
