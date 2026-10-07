import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'

import { routes } from './routes'

/**
 * Uygulamanın router örneğini oluşturur.
 *
 * Testler bellek geçmişiyle bağımsız router örnekleri oluşturabilsin diye
 * fabrika fonksiyonu olarak sunulur.
 *
 * @param {{ memory?: boolean }} [options] memory true ise tarayıcı adresi yerine bellek geçmişi kullanılır.
 * @returns {import('vue-router').Router} Router örneği.
 */
export function createAppRouter({ memory = false } = {}) {
  return createRouter({
    history: memory ? createMemoryHistory() : createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior: () => ({ top: 0 }),
  })
}
