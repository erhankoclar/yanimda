import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

import { installAdminUiGuard } from '@/admin/installAdminUiGuard'
import App from '@/App.vue'
import { createAppRouter } from '@/router'

/**
 * Uygulamayı yeni bir Pinia ve bellek geçmişli gerçek router ile verilen adreste bağlar.
 *
 * Gerçek uygulamadaki gibi admin arayüzü guard'ı router'dan önce kurulur; ilk
 * yönlendirme router uygulamaya bağlanırken yapılır.
 *
 * @param {string} path Açılacak adres.
 * @returns {Promise<{ wrapper: import('@vue/test-utils').VueWrapper, router: import('vue-router').Router, pinia: import('pinia').Pinia }>}
 *   Bağlanmış uygulama, router ve Pinia.
 */
export async function mountApp(path) {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = createAppRouter({ pinia, memory: true, initialPath: path })
  const adminUi = { install: (app) => installAdminUiGuard(router, app) }
  const wrapper = mount(App, { global: { plugins: [pinia, adminUi, router] }, attachTo: document.body })
  await router.isReady()
  await flushPromises()
  return { wrapper, router, pinia }
}
