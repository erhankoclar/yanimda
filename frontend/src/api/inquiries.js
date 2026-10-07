import { http } from './http'

export const inquiriesApi = {
  /**
   * Hesapsız hızlı talebi gönderir.
   *
   * @param {{ full_name: string, email: string, service: number, message: string, consent: boolean, website: string }} payload Form verisi.
   * @returns {Promise<{ id: number, created_at: string }>} Sunucuda kaydedilen talep.
   */
  create: (payload) => http.post('/inquiries/', payload, { skipAuthRefresh: true }).then((response) => response.data),
}
