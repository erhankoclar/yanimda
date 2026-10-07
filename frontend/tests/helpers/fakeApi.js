import { AxiosError } from 'axios'

import { http } from '@/api/http'

/**
 * http istemcisinin adapter'ını sahte bir işleyiciyle değiştirir; gerçek ağ isteği yapılmaz.
 *
 * İşleyici `[status, data]` döndürür. 2xx dışındaki durumlar axios'taki gibi
 * AxiosError olarak fırlatılır.
 *
 * @param {(config: import('axios').InternalAxiosRequestConfig) => [number, any] | Promise<[number, any]>} handler
 *   İsteği yanıtlayan fonksiyon.
 * @returns {Array<import('axios').InternalAxiosRequestConfig>} Yapılan isteklerin kaydı.
 */
export function useFakeApi(handler) {
  const calls = []
  http.defaults.adapter = async (config) => {
    calls.push(config)
    const [status, data] = await handler(config)
    const response = { data, status, statusText: String(status), headers: {}, config, request: {} }
    if (status >= 200 && status < 300) return response
    throw new AxiosError(`HTTP ${status}`, String(status), config, {}, response)
  }
  return calls
}

/**
 * Testlerin varsayılan sahte API'si: hizmet listesi boş döner, diğer her istek 404'tür.
 * Hiçbir test gerçek ağa çıkmaz.
 *
 * @param {import('axios').InternalAxiosRequestConfig} config İstek ayarları.
 * @returns {[number, any]} Durum kodu ve gövde.
 */
export function defaultHandler(config) {
  if (config.method === 'get' && config.url === '/services/') return [200, []]
  return [404, { detail: 'Not found.' }]
}

/** Varsayılan sahte API'ye geri döner. */
export function restoreApi() {
  useFakeApi(defaultHandler)
}

/**
 * Yöntem ve yolu `GET /auth/me/` biçiminde eşleştiren işleyici oluşturur.
 *
 * @param {Record<string, (config: any) => [number, any]>} routes Anahtarı "YÖNTEM /yol" olan yanıtlayıcılar.
 * @returns {(config: any) => [number, any]} useFakeApi için işleyici; eşleşme yoksa 404 döner.
 */
export function routeHandler(routes) {
  return (config) => {
    const key = `${config.method.toUpperCase()} ${config.url.split('?')[0]}`
    const responder = routes[key]
    return responder ? responder(config) : [404, { detail: 'Not found.' }]
  }
}

export const APPLICANT = { id: 1, email: 'ayse@example.com', first_name: 'Ayşe', last_name: 'Yılmaz', phone: '', is_staff: false }
export const ADMIN = { id: 2, email: 'admin@example.com', first_name: 'Yönetici', last_name: '', phone: '', is_staff: true }
