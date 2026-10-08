/**
 * Testler için API biçiminde başvuru nesnesi üretir.
 *
 * @param {Record<string, any>} [overrides] Varsayılan alanları ezen değerler.
 * @returns {Record<string, any>} Başvuru.
 */
export function makeRequest(overrides = {}) {
  return {
    id: 21,
    service_detail: { id: 3, name: 'Refakat ve sohbet', slug: 'refakat', description: 'd', icon: 'companion' },
    elder_full_name: 'Fatma Yılmaz',
    elder_age: 78,
    relationship: 'parent',
    elder_notes: '',
    preferred_date: '2026-10-10',
    time_slot: 'morning',
    location: {
      district: { id: 5, name: 'Kadıköy', osm_id: 1005 },
      neighborhood: { id: 11, name: 'Caferağa Mahallesi', osm_id: 2011 },
    },
    address: 'Örnek Mah. No: 1',
    contact_phone: '05551112233',
    alternate_contact_name: '',
    alternate_contact_phone: '',
    status: 'new',
    status_display: 'Yeni',
    created_at: '2026-10-07T10:00:00+03:00',
    ...overrides,
  }
}

/**
 * Sayfalı API yanıtı üretir.
 *
 * @param {Array<object>} results Sonuçlar.
 * @param {string | null} [next] Sonraki sayfa adresi.
 * @returns {{ count: number, next: string | null, previous: null, results: Array<object> }} Sayfa.
 */
export function page(results, next = null) {
  return { count: results.length, next, previous: null, results }
}
