import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

import App from '@/App.vue'
import { createAppRouter } from '@/router'

/**
 * Uygulamayı yeni bir Pinia ve bellek geçmişli gerçek router ile verilen adreste bağlar.
 *
 * @param {string} path Açılacak adres.
 * @returns {Promise<{ wrapper: import('@vue/test-utils').VueWrapper, router: import('vue-router').Router, pinia: import('pinia').Pinia }>}
 *   Bağlanmış uygulama, router ve Pinia.
 */
export async function mountApp(path) {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = createAppRouter({ pinia, memory: true })
  router.push(path)
  await router.isReady()
  const wrapper = mount(App, { global: { plugins: [pinia, router] }, attachTo: document.body })
  await flushPromises()
  return { wrapper, router, pinia }
}
