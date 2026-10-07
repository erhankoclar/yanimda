import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi } from '@/api/auth'
import { onSessionExpired } from '@/api/http'
import { tokenStorage } from '@/api/tokenStorage'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const initialized = ref(false)
  let initPromise = null

  // Oturum durumu tek kaynaktan (user) türetilir.
  const isAuthenticated = computed(() => user.value !== null)
  // Admin paneline erişim backend'deki is_staff bayrağına bağlıdır.
  const isAdmin = computed(() => user.value?.is_staff === true)
  // Üst barda gösterilecek ad; ad yoksa e-posta kullanılır.
  const displayName = computed(() => {
    if (!user.value) return ''
    const fullName = `${user.value.first_name ?? ''} ${user.value.last_name ?? ''}`.trim()
    return fullName || user.value.email
  })

  /**
   * Saklı token varsa kullanıcıyı yükler; uygulama ömründe bir kez çalışır.
   *
   * @returns {Promise<void>}
   */
  function init() {
    if (!initPromise) {
      initPromise = (tokenStorage.getAccess() || tokenStorage.getRefresh() ? fetchMe() : Promise.resolve())
        .catch(() => clearSession())
        .finally(() => {
          initialized.value = true
        })
    }
    return initPromise
  }

  /**
   * Oturumdaki kullanıcının profilini sunucudan okur.
   *
   * @returns {Promise<object>} Kullanıcı profili.
   */
  async function fetchMe() {
    user.value = await authApi.me()
    return user.value
  }

  /**
   * E-posta ve parolayla giriş yapar, token'ları saklar ve profili yükler.
   *
   * @param {string} email E-posta adresi.
   * @param {string} password Parola.
   * @returns {Promise<object>} Giriş yapan kullanıcı.
   */
  async function login(email, password) {
    const tokens = await authApi.login(email.trim(), password)
    tokenStorage.set(tokens)
    try {
      return await fetchMe()
    } catch (error) {
      clearSession()
      throw error
    }
  }

  /**
   * Yeni hesap oluşturur ve aynı bilgilerle giriş yapar.
   *
   * @param {{ email: string, password: string, first_name: string, last_name: string, phone?: string }} payload Kayıt bilgileri.
   * @returns {Promise<object>} Kayıt olan kullanıcı.
   */
  async function register(payload) {
    await authApi.register(payload)
    return login(payload.email, payload.password)
  }

  /** Token'ları ve kullanıcı bilgisini temizler. */
  function clearSession() {
    tokenStorage.clear()
    user.value = null
  }

  /**
   * Oturumu sunucuda sonlandırır ve yerel oturumu temizler.
   *
   * Sunucuya ulaşılamasa bile yerel token'lar silinir; kullanıcı çıkmış sayılır.
   *
   * @returns {Promise<void>}
   */
  async function logout() {
    const refresh = tokenStorage.getRefresh()
    clearSession()
    if (refresh) {
      await authApi.logout(refresh).catch(() => {})
    }
  }

  onSessionExpired(() => {
    user.value = null
  })

  return { user, initialized, isAuthenticated, isAdmin, displayName, init, fetchMe, login, register, logout }
})
