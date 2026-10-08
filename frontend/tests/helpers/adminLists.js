// Admin liste ve detay ekranı testleri için kurgusal veriler ve ortak yardımcılar.

import { flushPromises } from '@vue/test-utils'
import { expect, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { ADMIN, routeHandler, useFakeApi } from './fakeApi'
import { inquiryRow, requestRow } from './map'

export const SERVICES = [
  { id: 1, name: 'Evde bakım', icon: 'home-care', slug: 'evde-bakim', description: 'd' },
  { id: 2, name: 'Alışveriş desteği', icon: 'shopping', slug: 'alisveris', description: 'd' },
]

/**
 * Hızlı talep listesi/detay nesnesi üretir.
 *
 * @param {number} id Kimlik.
 * @param {Record<string, any>} [overrides] Alan değişiklikleri.
 * @returns {object} Hızlı talep.
 */
export function inquiryItem(id, overrides = {}) {
  return {
    ...inquiryRow(id),
    email: `kisi${id}@example.com`,
    message: `Annem için ${id} numaralı destek talebi, haftada iki gün.`,
    consent_given_at: '2026-10-07T10:00:00+03:00',
    ...overrides,
  }
}

/**
 * Başvuru listesi satırı üretir.
 *
 * @param {number} id Kimlik.
 * @param {Record<string, any>} [overrides] Alan değişiklikleri.
 * @returns {object} Satır.
 */
export function requestListItem(id, overrides = {}) {
  return {
    ...requestRow(id),
    elder_age: 78,
    preferred_date: '2026-10-12',
    time_slot_display: 'Sabah',
    contact_phone: '05551112233',
    applicant: { id: 30, email: 'ayse@example.com', full_name: 'Ayşe Yılmaz' },
    ...overrides,
  }
}

/**
 * Başvuru detay nesnesi üretir.
 *
 * @param {Record<string, any>} [overrides] Alan değişiklikleri.
 * @returns {object} Detay.
 */
export function requestDetail(overrides = {}) {
  return {
    ...requestListItem(7),
    elder_notes: 'Yürürken desteğe ihtiyaç duyuyor.',
    relationship_display: 'Anne/baba',
    address: 'Örnek Mah. No: 1',
    alternate_contact_name: '',
    alternate_contact_phone: '',
    consent_given_at: '2026-10-07T10:00:00+03:00',
    updated_at: '2026-10-07T11:00:00+03:00',
    admin_note: '',
    next_statuses: ['reviewing', 'cancelled'],
    applicant: { id: 30, email: 'ayse@example.com', full_name: 'Ayşe Yılmaz', phone: '05550000000' },
    ...overrides,
  }
}

/**
 * Kullanıcı listesi/detay nesnesi üretir.
 *
 * @param {number} id Kimlik.
 * @param {Record<string, any>} [overrides] Alan değişiklikleri.
 * @returns {object} Kullanıcı.
 */
export function userItem(id, overrides = {}) {
  return {
    id,
    email: `kullanici${id}@example.com`,
    full_name: `Kullanıcı ${id}`,
    phone: '05553334455',
    is_staff: false,
    is_active: true,
    request_count: 3,
    date_joined: '2026-09-01T09:00:00+03:00',
    last_login: '2026-10-05T09:00:00+03:00',
    ...overrides,
  }
}

/**
 * Sayfalı yanıt üretir.
 *
 * @param {Array<object>} results Sonuçlar.
 * @param {number} [count] Toplam kayıt; verilmezse sonuç sayısı.
 * @returns {{ count: number, results: Array<object> }} Yanıt.
 */
export function paged(results, count = results.length) {
  return { count, next: null, previous: null, results }
}

/**
 * Yönetici oturumu açılmış gibi token ve sahte API hazırlar; hizmet listesi de yanıtlanır.
 *
 * @param {Record<string, (config: any) => [number, any]>} [routes] Ek yanıtlayıcılar ("YÖNTEM /yol").
 * @returns {Array<object>} İstek kaydı.
 */
export function adminSession(routes = {}) {
  tokenStorage.set({ access: 'a1', refresh: 'r1' })
  return useFakeApi(routeHandler({
    'GET /auth/me/': () => [200, ADMIN],
    'GET /services/': () => [200, SERVICES],
    ...routes,
  }))
}

/**
 * Belirli bir adrese yapılan istekleri döndürür.
 *
 * @param {Array<object>} calls İstek kaydı.
 * @param {string} method HTTP yöntemi (küçük harf).
 * @param {string} url Yol.
 * @returns {Array<object>} Eşleşen istekler.
 */
export function callsTo(calls, method, url) {
  return calls.filter((call) => call.method === method && call.url.split('?')[0] === url)
}

/**
 * Tablo satırları görünene kadar bekler.
 *
 * @param {import('@vue/test-utils').VueWrapper} wrapper Uygulama.
 * @param {number} [count] Beklenen en az satır sayısı.
 */
export async function waitForRows(wrapper, count = 1) {
  await vi.waitFor(() => expect(wrapper.findAll('tbody tr:not(.p-datatable-empty-message)').length).toBeGreaterThanOrEqual(count), { timeout: 5000 })
}

/**
 * Bir PrimeVue Select'i erişilebilir adıyla bulup açar ve seçeneği tıklar.
 *
 * @param {import('@vue/test-utils').VueWrapper} wrapper Uygulama.
 * @param {string} ariaLabel Select'in aria-label değeri.
 * @param {string} optionText Seçilecek seçeneğin görünen metni.
 */
export async function chooseOption(wrapper, ariaLabel, optionText) {
  const label = wrapper.get(`[aria-label="${ariaLabel}"]`)
  await label.element.closest('.p-select').dispatchEvent(new MouseEvent('click', { bubbles: true }))
  await flushPromises()
  let option
  await vi.waitFor(() => {
    option = [...document.body.querySelectorAll('[role="option"]')].find((item) => item.textContent.trim() === optionText)
    expect(option).toBeTruthy()
  }, { timeout: 3000 })
  option.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
  await flushPromises()
}

/**
 * Tembel yüklenen admin sayfalarını önceden içe aktarır; yoğun makinede ilk testin zaman aşımına
 * uğramasını önlemek için `beforeAll` içinde çağrılır.
 *
 * @returns {Promise<void>} Sayfalar yüklenince çözülür.
 */
export async function warmAdminViews() {
  await Promise.all([
    import('@/views/admin/DashboardView.vue'),
    import('@/views/admin/InquiriesView.vue'),
    import('@/views/admin/RequestsView.vue'),
    import('@/views/admin/RequestDetailView.vue'),
    import('@/views/admin/UsersView.vue'),
    import('@/views/admin/UserDetailView.vue'),
  ])
}
