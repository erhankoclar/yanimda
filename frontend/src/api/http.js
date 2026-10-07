import axios from 'axios'

import { tokenStorage } from './tokenStorage'

export const API_BASE_URL = '/api'
const REFRESH_URL = '/auth/token/refresh/'

// Backend doğrulama mesajları arayüz diliyle aynı (Türkçe) gelsin.
export const http = axios.create({ baseURL: API_BASE_URL, timeout: 15000, headers: { 'Accept-Language': 'tr' } })

const sessionExpiredListeners = new Set()

/**
 * Oturum yenilenemediğinde çağrılacak dinleyiciyi kaydeder.
 *
 * @param {() => void} listener Oturum düştüğünde çalışacak fonksiyon.
 * @returns {() => void} Dinleyiciyi kaldıran fonksiyon.
 */
export function onSessionExpired(listener) {
  sessionExpiredListeners.add(listener)
  return () => sessionExpiredListeners.delete(listener)
}

/**
 * İsteğin kendi API'mize gidip gitmediğini söyler; token yalnızca bu isteklere eklenir.
 *
 * @param {import('axios').InternalAxiosRequestConfig} config İstek ayarları.
 * @returns {boolean} Göreli adres veya aynı köken ise true.
 */
function isOwnApiRequest(config) {
  const url = config.url ?? ''
  if (!/^[a-z][a-z\d+.-]*:|^\/\//i.test(url)) return true
  try {
    return new URL(url).origin === window.location.origin
  } catch {
    return false
  }
}

http.interceptors.request.use((config) => {
  const access = tokenStorage.getAccess()
  if (access && isOwnApiRequest(config)) {
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
})

let refreshPromise = null

/**
 * Refresh token ile yeni token çifti alır; eşzamanlı 401'ler tek isteği paylaşır.
 *
 * @returns {Promise<string>} Yeni access token.
 * @throws {Error} Refresh token yoksa veya yenileme başarısızsa.
 */
function refreshAccessToken() {
  if (!refreshPromise) {
    const refresh = tokenStorage.getRefresh()
    refreshPromise = (refresh
      ? http.post(REFRESH_URL, { refresh }, { skipAuthRefresh: true })
      : Promise.reject(new Error('refresh token yok')))
      .then(({ data }) => {
        tokenStorage.set(data)
        return data.access
      })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config
    const canRetry = error.response?.status === 401 && config && !config.skipAuthRefresh && !config._retried
    if (!canRetry || !tokenStorage.getRefresh()) {
      return Promise.reject(error)
    }
    try {
      const access = await refreshAccessToken()
      config._retried = true
      config.headers.Authorization = `Bearer ${access}`
      return http(config)
    } catch {
      tokenStorage.clear()
      sessionExpiredListeners.forEach((listener) => listener())
      return Promise.reject(error)
    }
  },
)
