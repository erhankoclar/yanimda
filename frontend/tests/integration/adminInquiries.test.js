import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'

import { adminSession, warmAdminViews, callsTo, chooseOption, inquiryItem, paged, waitForRows } from '../helpers/adminLists'
import { restoreApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

beforeAll(warmAdminViews, 90000)

afterEach(() => {
  wrapper?.unmount()
  document.body.innerHTML = ''
  restoreApi()
  window.localStorage.clear()
})

/**
 * Hızlı talep listesi ve detayını yanıtlayan oturum kurar.
 *
 * @param {Record<string, any>} [routes] Ek yanıtlayıcılar.
 * @param {number} [count] Liste toplamı.
 * @returns {Array<object>} İstek kaydı.
 */
function session(routes = {}, count = 2) {
  return adminSession({
    'GET /admin/inquiries/': () => [200, paged([inquiryItem(1), inquiryItem(2, { location: null })], count)],
    'GET /admin/inquiries/7/': () => [200, inquiryItem(7, { full_name: 'Zeynep Kaya', email: 'zeynep@example.com' })],
    ...routes,
  })
}

/**
 * Çekmece öğesini gövdeden bulur.
 *
 * @returns {HTMLElement | null} Çekmece.
 */
function drawer() {
  return document.body.querySelector('.inquiry-drawer')
}

describe('admin hızlı talepler listesi', () => {
  it('satırları ve konumsuz talebi gösterir', async () => {
    session()
    const mounted = await mountApp('/admin/inquiries')
    wrapper = mounted.wrapper

    await waitForRows(wrapper, 2)

    const text = wrapper.get('tbody').text()
    expect(text).toContain('Kişi 1')
    expect(text).toContain('kisi1@example.com')
    expect(text).toContain('Moda Mahallesi')
    expect(text).toContain('Alışveriş desteği')
    expect(wrapper.findAll('tbody tr')[1].text()).toContain('Yok')
  })

  it('boş sonuçta boş durum metnini gösterir', async () => {
    session({ 'GET /admin/inquiries/': () => [200, paged([])] })
    ;({ wrapper } = await mountApp('/admin/inquiries'))

    await vi.waitFor(() => expect(wrapper.text()).toContain('Bu seçimde kayıt yok.'), { timeout: 5000 })
  })

  it('arama yazısını gecikmeyle tek istek olarak gönderir ve adrese yazar', async () => {
    const calls = session()
    const mounted = await mountApp('/admin/inquiries')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)
    const before = callsTo(calls, 'get', '/admin/inquiries/').length

    const input = wrapper.get('.admin-list__search input')
    await input.setValue('z')
    await input.setValue('zey')
    expect(callsTo(calls, 'get', '/admin/inquiries/')).toHaveLength(before)

    await vi.waitFor(() => expect(callsTo(calls, 'get', '/admin/inquiries/')).toHaveLength(before + 1), { timeout: 3000 })
    expect(callsTo(calls, 'get', '/admin/inquiries/').at(-1).params).toEqual({ page: 1, search: 'zey' })
    expect(mounted.router.currentRoute.value.query.search).toBe('zey')
  })

  it('hizmet süzgecini seçince service parametresiyle yeniden listeler', async () => {
    const calls = session()
    const mounted = await mountApp('/admin/inquiries')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)

    await vi.waitFor(() => expect(wrapper.text()).toContain('Tüm hizmetler'))
    await chooseOption(wrapper, 'Hizmet', 'Evde bakım')

    await vi.waitFor(() => expect(callsTo(calls, 'get', '/admin/inquiries/').at(-1).params).toEqual({ page: 1, service: '1' }), { timeout: 3000 })
    expect(mounted.router.currentRoute.value.query.service).toBe('1')
  })

  it('ilçe süzgecini seçince district parametresiyle yeniden listeler', async () => {
    const calls = session()
    const mounted = await mountApp('/admin/inquiries')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)

    await chooseOption(wrapper, 'İlçe', 'Kadıköy')

    await vi.waitFor(() => expect(callsTo(calls, 'get', '/admin/inquiries/').at(-1).params).toEqual({ page: 1, district: '5' }), { timeout: 3000 })
  })

  it('adresteki süzgeç değerleriyle açılır', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/inquiries?search=ayse&service=2&page=2'))

    await waitForRows(wrapper)

    expect(callsTo(calls, 'get', '/admin/inquiries/')[0].params).toEqual({ page: 2, search: 'ayse', service: '2' })
    expect(wrapper.get('.admin-list__search input').element.value).toBe('ayse')
  })

  it('sonraki sayfa düğmesi page=2 ister', async () => {
    const calls = session({}, 45)
    const mounted = await mountApp('/admin/inquiries')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)

    await wrapper.get('.p-paginator-next').trigger('click')

    await vi.waitFor(() => expect(callsTo(calls, 'get', '/admin/inquiries/').at(-1).params).toEqual({ page: 2 }), { timeout: 3000 })
    expect(mounted.router.currentRoute.value.query.page).toBe('2')
  })

  it('liste hatasında uyarı ve Tekrar dene düğmesi gösterir', async () => {
    let fail = true
    session({ 'GET /admin/inquiries/': () => (fail ? [500, {}] : [200, paged([inquiryItem(1)])]) })
    ;({ wrapper } = await mountApp('/admin/inquiries'))

    await vi.waitFor(() => expect(wrapper.find('[role="alert"]').exists()).toBe(true), { timeout: 5000 })
    fail = false
    await wrapper.get('[role="alert"] button').trigger('click')

    await waitForRows(wrapper)
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
  })
})

describe('hızlı talep çekmecesi', () => {
  it('satıra tıklayınca çekmece açılır ve adrese id yazılır', async () => {
    session()
    const mounted = await mountApp('/admin/inquiries')
    wrapper = mounted.wrapper
    await waitForRows(wrapper, 2)

    await wrapper.findAll('tbody tr')[0].trigger('click')

    await vi.waitFor(() => expect(drawer()).toBeTruthy(), { timeout: 3000 })
    expect(drawer().textContent).toContain('Kişi 1')
    expect(drawer().textContent).toContain('kisi1@example.com')
    expect(drawer().textContent).toContain('Annem için 1 numaralı destek talebi')
    await vi.waitFor(() => expect(mounted.router.currentRoute.value.query.id).toBe('1'), { timeout: 3000 })
  })

  it('yanıtla bağlantısı konu satırı dolu bir mailto adresidir', async () => {
    session()
    const mounted = await mountApp('/admin/inquiries')
    wrapper = mounted.wrapper
    await waitForRows(wrapper, 2)

    await wrapper.findAll('tbody tr')[0].trigger('click')
    await vi.waitFor(() => expect(drawer()).toBeTruthy(), { timeout: 3000 })

    const link = drawer().querySelector('a[href^="mailto:"]')
    expect(link.textContent).toContain('E-posta ile yanıtla')
    expect(link.getAttribute('href')).toBe(
      `mailto:kisi1@example.com?subject=${encodeURIComponent('Yanımda: Alışveriş desteği talebiniz')}`,
    )
  })

  it('konumu olmayan talepte konum yerine Yok yazar', async () => {
    session()
    const mounted = await mountApp('/admin/inquiries')
    wrapper = mounted.wrapper
    await waitForRows(wrapper, 2)

    await wrapper.findAll('tbody tr')[1].trigger('click')
    await vi.waitFor(() => expect(drawer()).toBeTruthy(), { timeout: 3000 })

    expect(drawer().textContent).toContain('Yok')
  })

  it('/admin/inquiries?id=7 adresi talebi sunucudan okuyup çekmeceyi açar', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/inquiries?id=7'))

    await vi.waitFor(() => expect(drawer()).toBeTruthy(), { timeout: 5000 })

    expect(callsTo(calls, 'get', '/admin/inquiries/7/')).toHaveLength(1)
    expect(drawer().textContent).toContain('Zeynep Kaya')
    expect(drawer().querySelector('a[href^="mailto:zeynep@example.com"]')).toBeTruthy()
  })

  it('olmayan talepte "Bu hızlı talep bulunamadı." uyarısı gösterir ve çekmece açılmaz', async () => {
    session({ 'GET /admin/inquiries/99/': () => [404, { detail: 'Not found.' }] })
    ;({ wrapper } = await mountApp('/admin/inquiries?id=99'))

    await vi.waitFor(() => expect(wrapper.text()).toContain('Bu hızlı talep bulunamadı.'), { timeout: 5000 })

    expect(drawer()).toBeNull()
  })

  it('çekmece kapanınca adresten id kalkar', async () => {
    session()
    const mounted = await mountApp('/admin/inquiries?id=7')
    wrapper = mounted.wrapper
    await vi.waitFor(() => expect(drawer()).toBeTruthy(), { timeout: 5000 })

    document.body.querySelector('.p-drawer-close-button').click()
    await flushPromises()

    await vi.waitFor(() => expect(drawer()).toBeNull(), { timeout: 3000 })
    expect(mounted.router.currentRoute.value.query.id).toBeUndefined()
  })
})
