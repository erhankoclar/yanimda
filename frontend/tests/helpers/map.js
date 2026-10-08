// Admin talep haritası testleri için kurgusal API yanıtı ve küçük GeoJSON sınır dosyaları.

import { vi } from 'vitest'

import { resetBoundaryCache } from '@/admin/map/useMapData'

const HOME = { id: 1, name: 'Evde bakım', icon: 'home-care' }
const SHOP = { id: 2, name: 'Alışveriş desteği', icon: 'shopping' }

/**
 * Backend'in `/admin/map/` yanıtının şeklinde kurgusal veri üretir.
 *
 * Toplam 9 kayıt: Evde bakım 6, Alışveriş desteği 3; Kadıköy 7, Üsküdar 2, Adalar 0.
 *
 * @param {object} [overrides] Üst düzey alanları değiştirmek için.
 * @returns {object} Harita yanıtı.
 */
export function mapResponse(overrides = {}) {
  return {
    total: 9,
    services: [{ ...HOME, count: 6 }, { ...SHOP, count: 3 }],
    districts: [
      { id: 5, osm_id: 1005, name: 'Kadıköy', count: 7, by_service: { 1: 5, 2: 2 } },
      { id: 6, osm_id: 1006, name: 'Üsküdar', count: 2, by_service: { 1: 1, 2: 1 } },
      { id: 7, osm_id: 1007, name: 'Adalar', count: 0, by_service: {} },
    ],
    neighborhoods: [
      { id: 12, osm_id: 2012, name: 'Moda Mahallesi', district_id: 5, count: 4, by_service: { 1: 3, 2: 1 } },
      { id: 11, osm_id: 2011, name: 'Caferağa Mahallesi', district_id: 5, count: 3, by_service: { 1: 2, 2: 1 } },
      { id: 21, osm_id: 2021, name: 'Altunizade Mahallesi', district_id: 6, count: 2, by_service: { 1: 1, 2: 1 } },
    ],
    ...overrides,
  }
}

/**
 * Tek özellikli küçük bir FeatureCollection üretir.
 *
 * @param {Array<{ id: number, name: string }>} properties Özellik bilgileri.
 * @returns {object} GeoJSON koleksiyonu.
 */
function collection(properties) {
  return {
    type: 'FeatureCollection',
    features: properties.map((item) => ({
      type: 'Feature',
      properties: item,
      geometry: { type: 'Point', coordinates: [29, 41] },
    })),
  }
}

export const BOUNDARY_FILES = {
  'istanbul-districts.geojson': collection([{ id: 1005, name: 'Kadıköy' }, { id: 1006, name: 'Üsküdar' }, { id: 1007, name: 'Adalar' }]),
  'istanbul-neighborhoods.geojson': collection([{ id: 2011, name: 'Caferağa Mahallesi' }, { id: 2012, name: 'Moda Mahallesi' }, { id: 2021, name: 'Altunizade Mahallesi' }]),
  'istanbul-labels.geojson': collection([{ id: 1005, name: 'Kadıköy' }]),
}

/**
 * Sınır dosyalarını yanıtlayan sahte `fetch` kurar ve önbelleği temizler.
 *
 * @returns {import('vitest').Mock} Yapılan indirmeleri kaydeden sahte fetch.
 */
export function stubBoundaryFetch() {
  resetBoundaryCache()
  const fetchMock = vi.fn(async (url) => {
    const file = Object.keys(BOUNDARY_FILES).find((name) => String(url).endsWith(name))
    return file
      ? { ok: true, status: 200, json: async () => BOUNDARY_FILES[file] }
      : { ok: false, status: 404, json: async () => ({}) }
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

/**
 * Admin başvuru listesi satırı üretir.
 *
 * @param {number} id Kimlik.
 * @param {Record<string, any>} [overrides] Alan değişiklikleri.
 * @returns {object} Satır.
 */
export function requestRow(id, overrides = {}) {
  return {
    id,
    service: HOME,
    elder_full_name: `Yaşlı ${id}`,
    location: { district: { id: 5, name: 'Kadıköy' }, neighborhood: { id: 12, name: 'Moda Mahallesi' } },
    status: 'new',
    created_at: '2026-10-07T10:00:00+03:00',
    ...overrides,
  }
}

/**
 * Admin hızlı talep listesi satırı üretir.
 *
 * @param {number} id Kimlik.
 * @param {Record<string, any>} [overrides] Alan değişiklikleri.
 * @returns {object} Satır.
 */
export function inquiryRow(id, overrides = {}) {
  return {
    id,
    service: SHOP,
    full_name: `Kişi ${id}`,
    location: { district: { id: 5, name: 'Kadıköy' }, neighborhood: { id: 12, name: 'Moda Mahallesi' } },
    created_at: '2026-10-07T10:00:00+03:00',
    ...overrides,
  }
}

/**
 * jsdom'da olmayan `window.matchMedia` için sabit bir taklit kurar (PrimeVue Select ihtiyaç duyar).
 *
 * @returns {() => void} Taklidi kaldıran fonksiyon.
 */
export function stubMatchMedia() {
  window.matchMedia = (query) => ({
    matches: false, media: query, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {},
  })
  return () => { delete window.matchMedia }
}
