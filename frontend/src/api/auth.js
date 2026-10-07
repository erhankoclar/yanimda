import { http } from './http'

export const authApi = {
  /** @param {{ email: string, password: string, first_name: string, last_name: string, phone?: string }} payload */
  register: (payload) => http.post('/auth/register/', payload).then((response) => response.data),
  /** @returns {Promise<{ access: string, refresh: string }>} */
  login: (email, password) => http.post('/auth/token/', { email, password }, { skipAuthRefresh: true })
    .then((response) => response.data),
  me: () => http.get('/auth/me/').then((response) => response.data),
  /** @param {{ first_name?: string, last_name?: string, phone?: string }} payload */
  updateMe: (payload) => http.patch('/auth/me/', payload).then((response) => response.data),
}
