/**
 * Admin route'una ilk girişte PrimeVue kurulumunu tembel yükleyen guard'ı ekler.
 *
 * @param {import('vue-router').Router} router Uygulama router'ı.
 * @param {import('vue').App} app Kurulumun yapılacağı Vue uygulaması.
 */
export function installAdminUiGuard(router, app) {
  let ready = null
  router.beforeEach(async (to) => {
    if (!to.matched.some((record) => record.meta.area === 'admin')) return true
    if (!ready) {
      // Kurulum tek sefer yapılır; eşzamanlı geçişler aynı yüklemeyi bekler.
      ready = import('./setupAdminUi').then(({ setupAdminUi }) => setupAdminUi(app))
    }
    await ready
    return true
  })
}
