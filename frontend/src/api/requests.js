import { http } from './http'

export const requestsApi = {
  /** @returns {Promise<Array<{ id: number, name: string, slug: string, description: string, icon: string }>>} Aktif hizmetler. */
  services: () => http.get('/services/').then((response) => response.data),
  /** @param {number} [page] Sayfa numarası. @returns {Promise<{ count: number, next: string|null, previous: string|null, results: Array<object> }>} */
  list: (page = 1) => http.get('/requests/', { params: { page } }).then((response) => response.data),
  /** @param {number|string} id Başvuru kimliği. */
  get: (id) => http.get(`/requests/${id}/`).then((response) => response.data),
  /** @param {object} payload Başvuru verileri. */
  create: (payload) => http.post('/requests/', payload).then((response) => response.data),
}
