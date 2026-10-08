import { useAuthStore } from '@/stores/auth'

/**
 * Oturum ve yetki kurallarını uygulayan global route guard'ını kurar.
 *
 * - `requiresAdmin`: admin olmayanlar admin girişine yönlenir.
 * - `requiresAuth`: oturumsuz kullanıcılar girişe yönlenir.
 * - `guestOnly`: oturumu açık kullanıcılar ilgili ana sayfaya yönlenir (yönetici her zaman yönetim paneline).
 *
 * @param {import('vue-router').Router} router Uygulama router'ı.
 * @param {import('pinia').Pinia} pinia Store'ların bağlı olduğu Pinia örneği.
 */
export function installGuards(router, pinia) {
  router.beforeEach(async (to) => {
    const auth = useAuthStore(pinia)
    await auth.init()

    if (to.matched.some((record) => record.meta.requiresAdmin) && !auth.isAdmin) {
      return { name: 'admin-login', query: { redirect: to.fullPath } }
    }
    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    if (to.meta.guestOnly && auth.isAuthenticated) {
      if (to.meta.area === 'admin') {
        return auth.isAdmin ? { name: 'admin-dashboard' } : true
      }
      // Yönetici genel giriş sayfasına gelirse doğrudan yönetim paneline gider.
      return auth.isAdmin ? { name: 'admin-dashboard' } : { name: 'request-list' }
    }
    return true
  })
}
