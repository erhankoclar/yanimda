/**
 * Admin arayüzünün PrimeVue kurulumu.
 *
 * PrimeVue yalnızca admin tarafında kullanılır. Bu modül yalnızca admin
 * route'larına ilk girişte dinamik olarak yüklenir; böylece PrimeVue ve tema
 * son kullanıcı sayfalarının paketlerine hiç girmez.
 */
import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'
import PrimeVue from 'primevue/config'
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'

import 'primeicons/primeicons.css'
import '@/styles/admin.css'

import { trLocale } from './trLocale'

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
  },
})

/**
 * PrimeVue'yu, Toast ve onay servislerini uygulamaya kurar.
 *
 * @param {import('vue').App} app Vue uygulaması.
 */
export function setupAdminUi(app) {
  app.use(PrimeVue, {
    theme: { preset: YanimdaPreset, options: { darkModeSelector: false, cssLayer: false } },
    locale: trLocale,
  })
  app.use(ToastService)
  app.use(ConfirmationService)
}
