// Admin gösterge paneli testleri için kurgusal API yanıtı.

const HOME = { id: 1, name: 'Evde bakım', icon: 'home-care' }
const SHOP = { id: 2, name: 'Alışveriş desteği', icon: 'shopping' }

/**
 * Backend'in `/admin/dashboard/` yanıtının şeklinde kurgusal veri üretir.
 *
 * @param {object} [overrides] Üst düzey alanları değiştirmek için.
 * @returns {object} Dashboard yanıtı.
 */
export function dashboardResponse(overrides = {}) {
  return {
    cards: {
      total_demand: { value: 1250, previous: 1000, change_percent: 25 },
      open_requests: { value: 7, new: 3 },
      inquiries: { value: 40, previous: 50, change_percent: -20 },
      services: { value: 6, top_service: 'Evde bakım' },
    },
    series: {
      bucket: 'day',
      labels: ['2026-10-06', '2026-10-07', '2026-10-08'],
      datasets: [
        { service_id: 1, name: HOME.name, icon: HOME.icon, counts: [1, 0, 2] },
        { service_id: 2, name: SHOP.name, icon: SHOP.icon, counts: [0, 3, 1] },
      ],
    },
    recent: [
      { type: 'request', id: 21, title: 'Fatma Demir', service: HOME, created_at: '2026-10-08T09:30:00+03:00', status: 'new' },
      { type: 'inquiry', id: 5, title: 'Mehmet Kaya', service: SHOP, created_at: '2026-10-08T08:00:00+03:00', status: null },
    ],
    pending: [
      { id: 21, service: HOME, elder_full_name: 'Fatma Demir', preferred_date: '2026-10-12', status: 'new', created_at: '2026-10-01T10:00:00+03:00' },
    ],
    status_breakdown: [
      { status: 'new', label: 'Alındı', count: 3 },
      { status: 'reviewing', label: 'İnceleniyor', count: 2 },
      { status: 'assigned', label: 'Kişi atandı', count: 2 },
      { status: 'completed', label: 'Tamamlandı', count: 5 },
      { status: 'cancelled', label: 'İptal edildi', count: 1 },
    ],
    ...overrides,
  }
}
