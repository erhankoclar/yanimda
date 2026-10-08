import { http } from './http'

const data = (response) => response.data

export const adminApi = {
  /**
   * @param {{ days?: 7 | 30 | 90, source?: 'all' | 'inquiries' | 'requests' }} [params] Grafik seçimi.
   */
  dashboard: (params = {}) => http.get('/admin/dashboard/', { params }).then(data),
  /**
   * @param {{ source?: 'all' | 'inquiries' | 'requests', days?: number }} [params] Kaynak ve dönem.
   * @returns {Promise<{ total: number, services: Array<object>, districts: Array<object>, neighborhoods: Array<object> }>}
   *   İlçe ve mahalle bazında, hizmet dağılımlı sayılar.
   */
  map: (params = {}) => http.get('/admin/map/', { params }).then(data),
  /** @param {Record<string, any>} [params] Filtre, arama, sıralama ve sayfa. */
  requests: (params = {}) => http.get('/admin/requests/', { params }).then(data),
  /** @param {number|string} id Başvuru kimliği. */
  request: (id) => http.get(`/admin/requests/${id}/`).then(data),
  /**
   * @param {number|string} id Başvuru kimliği.
   * @param {{ status?: string, admin_note?: string }} changes Değişiklikler.
   */
  updateRequest: (id, changes) => http.patch(`/admin/requests/${id}/`, changes).then(data),
  /** @param {Record<string, any>} [params] Arama, hizmet ve sayfa. */
  inquiries: (params = {}) => http.get('/admin/inquiries/', { params }).then(data),
  /** @param {Record<string, any>} [params] Arama, filtre, sıralama ve sayfa. */
  users: (params = {}) => http.get('/admin/users/', { params }).then(data),
  /** @param {number|string} id Kullanıcı kimliği. */
  user: (id) => http.get(`/admin/users/${id}/`).then(data),
}
