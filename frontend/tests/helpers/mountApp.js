import { flushPromises, mount } from '@vue/test-utils'

import App from '@/App.vue'
import { createAppRouter } from '@/router'

/**
 * Uygulamayı bellek geçmişli gerçek router ile verilen adreste bağlar.
 *
 * @param {string} path Açılacak adres.
 * @param {{ plugins?: Array<any> }} [options] Router'a ek olarak kurulacak eklentiler.
 * @returns {Promise<{ wrapper: import('@vue/test-utils').VueWrapper, router: import('vue-router').Router }>}
 *   Bağlanmış uygulama ve router.
 */
export async function mountApp(path, { plugins = [] } = {}) {
  const router = createAppRouter({ memory: true })
  router.push(path)
  await router.isReady()
  const wrapper = mount(App, { global: { plugins: [...plugins, router] }, attachTo: document.body })
  await flushPromises()
  return { wrapper, router }
}
