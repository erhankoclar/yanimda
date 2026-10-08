import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'

import { adminSession, warmAdminViews, callsTo, chooseOption, paged, requestDetail, requestListItem, waitForRows } from '../helpers/adminLists'
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
 * Başvuru listesini yanıtlayan yönetici oturumu kurar.
 *
 * @param {Record<string, any>} [routes] Ek yanıtlayıcılar.
 * @param {number} [count] Liste toplamı.
 * @returns {Array<object>} İstek kaydı.
 */
function session(routes = {}, count = 2) {
  return adminSession({
    'GET /admin/requests/': () => [200, paged([requestListItem(5), requestListItem(6, { status: 'reviewing', elder_full_name: 'Hasan Demir' })], count)],
    'GET /admin/requests/5/': () => [200, requestDetail({ id: 5 })],
    ...routes,
  })
}

/**
 * Başvuru listesine yapılan son isteğin parametrelerini döndürür.
 *
 * @param {Array<object>} calls İstek kaydı.
 * @returns {Record<string, any>} Parametreler.
 */
function lastParams(calls) {
  return callsTo(calls, 'get', '/admin/requests/').at(-1).params
}

describe('admin başvurular listesi', () => {
  it('satır alanlarını gösterir', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/requests'))

    await waitForRows(wrapper, 2)

    const text = wrapper.get('tbody').text()
    expect(text).toContain('Yaşlı 5')
    expect(text).toContain('78 yaşında')
    expect(text).toContain('Evde bakım')
    expect(text).toContain('Moda Mahallesi')
    expect(text).toContain('Ayşe Yılmaz')
    expect(text).toContain('05551112233')
    expect(text).toContain('Alındı')
    expect(text).toContain('İnceleniyor')
  })

  it('ilk istekte yalnızca sayfa 1 gönderir', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/requests'))
    await waitForRows(wrapper)

    expect(callsTo(calls, 'get', '/admin/requests/')[0].params).toEqual({ page: 1, ordering: '-created_at' })
  })

  it('arama yazısı gecikmeyle tek istek olarak search parametresine gider', async () => {
    const calls = session()
    const mounted = await mountApp('/admin/requests')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)
    const before = callsTo(calls, 'get', '/admin/requests/').length

    const input = wrapper.get('.admin-list__search input')
    await input.setValue('has')
    await input.setValue('hasan')
    expect(callsTo(calls, 'get', '/admin/requests/')).toHaveLength(before)

    await vi.waitFor(() => expect(callsTo(calls, 'get', '/admin/requests/')).toHaveLength(before + 1), { timeout: 3000 })
    expect(lastParams(calls)).toEqual({ page: 1, search: 'hasan', ordering: '-created_at' })
    expect(mounted.router.currentRoute.value.query.search).toBe('hasan')
  })

  it('durum süzgeci status parametresini gönderir', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/requests'))
    await waitForRows(wrapper)

    await chooseOption(wrapper, 'Durum', 'İnceleniyor')

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, status: 'reviewing', ordering: '-created_at' }), { timeout: 3000 })
  })

  it('hizmet ve ilçe süzgeçleri birlikte uygulanır', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/requests'))
    await waitForRows(wrapper)

    await chooseOption(wrapper, 'Hizmet', 'Alışveriş desteği')
    await chooseOption(wrapper, 'İlçe', 'Üsküdar')

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, service: '2', district: '6', ordering: '-created_at' }), { timeout: 3000 })
  })

  it('tarih aralığı seçilince created_from ve created_to gönderilir', async () => {
    const calls = session()
    const mounted = await mountApp('/admin/requests')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)

    wrapper.findComponent({ name: 'DatePicker' }).vm.$emit('update:modelValue', [new Date(2026, 9, 1), new Date(2026, 9, 5)])

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, created_from: '2026-10-01', created_to: '2026-10-05', ordering: '-created_at' }), { timeout: 3000 })
    expect(mounted.router.currentRoute.value.query).toMatchObject({ created_from: '2026-10-01', created_to: '2026-10-05' })
  })

  it('yalnızca başlangıç seçilince bitiş aynı gün olur', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/requests'))
    await waitForRows(wrapper)

    wrapper.findComponent({ name: 'DatePicker' }).vm.$emit('update:modelValue', [new Date(2026, 9, 3), null])

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, created_from: '2026-10-03', created_to: '2026-10-03', ordering: '-created_at' }), { timeout: 3000 })
  })

  it('tarih aralığı temizlenince parametreler kalkar', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/requests?created_from=2026-10-01&created_to=2026-10-05'))
    await waitForRows(wrapper)
    expect(lastParams(calls)).toEqual({ page: 1, created_from: '2026-10-01', created_to: '2026-10-05', ordering: '-created_at' })

    wrapper.findComponent({ name: 'DatePicker' }).vm.$emit('update:modelValue', null)

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, ordering: '-created_at' }), { timeout: 3000 })
  })

  it('adresteki süzgeçlerle açılır', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/requests?status=new&ordering=-preferred_date&page=2'))
    await waitForRows(wrapper)

    expect(callsTo(calls, 'get', '/admin/requests/')[0].params).toEqual({ page: 2, status: 'new', ordering: '-preferred_date' })
  })

  it('sütun başlığına tıklayınca sırasıyla artan, azalan ve varsayılan sırayı ister', async () => {
    const calls = session()
    const mounted = await mountApp('/admin/requests')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)
    const header = () => wrapper.findAll('th').find((item) => item.text().includes('Tercih edilen gün'))

    await header().trigger('click')
    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, ordering: 'preferred_date' }), { timeout: 3000 })

    await header().trigger('click')
    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, ordering: '-preferred_date' }), { timeout: 3000 })
    expect(mounted.router.currentRoute.value.query.ordering).toBe('-preferred_date')

    await header().trigger('click')
    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, ordering: '-created_at' }), { timeout: 3000 })
  })

  it.each([
    ['Durum', 'status'],
  ])('%s sütunu %s alanına göre sıralanabilir', async (title, field) => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/requests'))
    await waitForRows(wrapper)

    await wrapper.findAll('th').find((item) => item.text() === title).trigger('click')

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, ordering: field }), { timeout: 3000 })
  })

  it('sonraki sayfa düğmesi page=2 ister', async () => {
    const calls = session({}, 45)
    ;({ wrapper } = await mountApp('/admin/requests'))
    await waitForRows(wrapper)

    await wrapper.get('.p-paginator-next').trigger('click')

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 2, ordering: '-created_at' }), { timeout: 3000 })
  })

  it('satıra tıklayınca başvuru detayına gider', async () => {
    session()
    const mounted = await mountApp('/admin/requests')
    wrapper = mounted.wrapper
    await waitForRows(wrapper, 2)
    const router = mounted.router

    await wrapper.findAll('tbody tr')[0].trigger('click')

    await vi.waitFor(() => expect(router.currentRoute.value.fullPath).toBe('/admin/requests/5'), { timeout: 5000 })
  })

  it('boş sonuçta boş durum metnini gösterir', async () => {
    session({ 'GET /admin/requests/': () => [200, paged([])] })
    ;({ wrapper } = await mountApp('/admin/requests'))

    await vi.waitFor(() => expect(wrapper.text()).toContain('Bu seçimde kayıt yok.'), { timeout: 5000 })
  })

  it('liste hatasında uyarı gösterir', async () => {
    session({ 'GET /admin/requests/': () => [500, {}] })
    ;({ wrapper } = await mountApp('/admin/requests'))

    await vi.waitFor(() => expect(wrapper.find('[role="alert"]').exists()).toBe(true), { timeout: 5000 })
    await flushPromises()
  })

  it('dil değişince liste yeniden istenir', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/requests'))
    await waitForRows(wrapper)
    const before = callsTo(calls, 'get', '/admin/requests/').length

    await wrapper.findAll('.preference-controls__flag')[1].trigger('click')

    await vi.waitFor(() => expect(callsTo(calls, 'get', '/admin/requests/').length).toBeGreaterThan(before), { timeout: 3000 })
  })
})
