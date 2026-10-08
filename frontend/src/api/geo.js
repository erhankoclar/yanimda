import { http } from './http'

export const geoApi = {
  /** @returns {Promise<Array<{ id: number, name: string, slug: string, osm_id: number }>>} İstanbul ilçeleri, Türkçe alfabe sırasıyla. */
  districts: () => http.get('/geo/districts/', { skipAuthRefresh: true }).then((response) => response.data),
  /**
   * @param {number} districtId İlçe kimliği.
   * @returns {Promise<Array<{ id: number, name: string, osm_id: number }>>} İlçenin mahalleleri.
   */
  neighborhoods: (districtId) => http.get(`/geo/districts/${districtId}/neighborhoods/`, { skipAuthRefresh: true })
    .then((response) => response.data),
}
