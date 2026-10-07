import { createMemoryHistory, createRouter, createWebHistory } from 'vue-router'

import { installGuards } from './guards'
import { routes } from './routes'

/**
 * Uygulamanın router örneğini guard'larıyla birlikte oluşturur.
 *
 * Testler bellek geçmişiyle bağımsız router örnekleri oluşturabilsin diye
 * fabrika fonksiyonu olarak sunulur.
 *
 * @param {{ pinia: import('pinia').Pinia, memory?: boolean }} options Pinia örneği ve geçmiş tercihi.
 * @returns {import('vue-router').Router} Router örneği.
 */
export function createAppRouter({ pinia, memory = false }) {
  const router = createRouter({
    history: memory ? createMemoryHistory() : createWebHistory(import.meta.env.BASE_URL),
    routes,
    // Bölüm bağlantıları (#hizmetler gibi) yapışkan üst barın altında kalmayacak şekilde kaydırılır.
    scrollBehavior: (to, from, savedPosition) => {
      if (savedPosition) return savedPosition
      if (to.hash) return { el: to.hash, top: 88, behavior: 'smooth' }
      return { top: 0 }
    },
  })
  installGuards(router, pinia)
  return router
}
