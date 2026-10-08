import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'

import { adminSession, warmAdminViews, callsTo, chooseOption, paged, requestDetail, requestListItem, userItem, waitForRows } from '../helpers/adminLists'
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
 * Kullanıcı listesini ve detayını yanıtlayan yönetici oturumu kurar.
 *
 * @param {Record<string, any>} [routes] Ek yanıtlayıcılar.
 * @param {number} [count] Liste toplamı.
 * @returns {Array<object>} İstek kaydı.
 */
function session(routes = {}, count = 2) {
  return adminSession({
    'GET /admin/users/': () => [200, paged([
      userItem(12, { full_name: 'Ayşe Yılmaz', email: 'ayse@example.com' }),
      userItem(13, { full_name: '', email: 'pasif@example.com', is_active: false, is_staff: true, last_login: null, request_count: 0 }),
    ], count)],
    'GET /admin/users/12/': () => [200, userItem(12, { full_name: 'Ayşe Yılmaz', email: 'ayse@example.com', request_count: 2 })],
    'GET /admin/requests/': () => [200, paged([requestListItem(5), requestListItem(6, { status: 'completed' })])],
    'GET /admin/requests/5/': () => [200, requestDetail({ id: 5 })],
    ...routes,
  })
}

/**
 * Kullanıcı listesine yapılan son isteğin parametrelerini döndürür.
 *
 * @param {Array<object>} calls İstek kaydı.
 * @returns {Record<string, any>} Parametreler.
 */
function lastParams(calls) {
  return callsTo(calls, 'get', '/admin/users/').at(-1).params
}

describe('admin kullanıcılar listesi', () => {
  it('satırları, rol ve kapalı hesap etiketlerini gösterir', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/users'))

    await waitForRows(wrapper, 2)

    const rows = wrapper.findAll('tbody tr')
    expect(rows[0].text()).toContain('Ayşe Yılmaz')
    expect(rows[0].text()).toContain('ayse@example.com')
    expect(rows[0].text()).toContain('Başvuru sahibi')
    expect(rows[1].text()).toContain('pasif@example.com')
    expect(rows[1].text()).toContain('Yönetici')
    expect(rows[1].text()).toContain('Kapalı hesap')
    expect(rows[1].text()).toContain('Hiç giriş yapmadı')
  })

  it('ilk istek varsayılan olarak en yeni kayıtları ister', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/users'))
    await waitForRows(wrapper)

    expect(callsTo(calls, 'get', '/admin/users/')[0].params).toEqual({ page: 1, ordering: '-date_joined' })
  })

  it('arama yazısı gecikmeyle tek istek olarak search parametresine gider', async () => {
    const calls = session()
    const mounted = await mountApp('/admin/users')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)
    const before = callsTo(calls, 'get', '/admin/users/').length

    const input = wrapper.get('.admin-list__search input')
    await input.setValue('ay')
    await input.setValue('ayse')
    expect(callsTo(calls, 'get', '/admin/users/')).toHaveLength(before)

    await vi.waitFor(() => expect(callsTo(calls, 'get', '/admin/users/')).toHaveLength(before + 1), { timeout: 3000 })
    expect(lastParams(calls)).toEqual({ page: 1, search: 'ayse', ordering: '-date_joined' })
    expect(mounted.router.currentRoute.value.query.search).toBe('ayse')
  })

  it.each([
    ['Yönetici', 'true'],
    ['Başvuru sahibi', 'false'],
  ])('rol süzgecinde %s seçilince is_staff=%s gönderilir', async (label, value) => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/users'))
    await waitForRows(wrapper)

    await chooseOption(wrapper, 'Rol', label)

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, is_staff: value, ordering: '-date_joined' }), { timeout: 3000 })
  })

  it.each([
    ['Açık hesap', 'true'],
    ['Kapalı hesap', 'false'],
  ])('hesap süzgecinde %s seçilince is_active=%s gönderilir', async (label, value) => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/users'))
    await waitForRows(wrapper)

    await chooseOption(wrapper, 'Hesap durumu', label)

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, is_active: value, ordering: '-date_joined' }), { timeout: 3000 })
  })

  it('adresteki süzgeçlerle açılır', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/users?is_staff=true&is_active=false&page=2&ordering=email'))
    await waitForRows(wrapper)

    expect(callsTo(calls, 'get', '/admin/users/')[0].params).toEqual({ page: 2, is_staff: 'true', is_active: 'false', ordering: 'email' })
  })

  it.each([
    ['Kullanıcı', 'email'],
    ['Başvuru', 'request_count'],
  ])('%s sütunu %s alanına artan, sonra azalan sıralanır', async (title, field) => {
    const calls = session()
    const mounted = await mountApp('/admin/users')
    wrapper = mounted.wrapper
    await waitForRows(wrapper)
    const header = () => wrapper.findAll('th').find((item) => item.text() === title)

    await header().trigger('click')
    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, ordering: field }), { timeout: 3000 })

    await header().trigger('click')
    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 1, ordering: `-${field}` }), { timeout: 3000 })
    expect(mounted.router.currentRoute.value.query.ordering).toBe(`-${field}`)
  })

  it('kayıt tarihi sütunu varsayılan olarak azalan sıralıdır ve ters sıralanabilir', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/users'))
    await waitForRows(wrapper)
    const header = wrapper.findAll('th').find((item) => item.text() === 'Kayıt tarihi')

    expect(header.attributes('aria-sort')).toBe('descending')
    await header.trigger('click')
    await vi.waitFor(() => expect(lastParams(calls).ordering).toBe('-date_joined'), { timeout: 3000 })
  })

  it('sonraki sayfa düğmesi page=2 ister', async () => {
    const calls = session({}, 45)
    ;({ wrapper } = await mountApp('/admin/users'))
    await waitForRows(wrapper)

    await wrapper.get('.p-paginator-next').trigger('click')

    await vi.waitFor(() => expect(lastParams(calls)).toEqual({ page: 2, ordering: '-date_joined' }), { timeout: 3000 })
  })

  it('satıra tıklayınca kullanıcı detayına gider', async () => {
    session()
    const mounted = await mountApp('/admin/users')
    wrapper = mounted.wrapper
    await waitForRows(wrapper, 2)

    await wrapper.findAll('tbody tr')[0].trigger('click')

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/admin/users/12'), { timeout: 5000 })
  })

  it('boş sonuçta boş durum metnini gösterir', async () => {
    session({ 'GET /admin/users/': () => [200, paged([])] })
    ;({ wrapper } = await mountApp('/admin/users'))

    await vi.waitFor(() => expect(wrapper.text()).toContain('Bu seçimde kayıt yok.'), { timeout: 5000 })
  })

  it('liste hatasında uyarı gösterir', async () => {
    session({ 'GET /admin/users/': () => [500, {}] })
    ;({ wrapper } = await mountApp('/admin/users'))

    await vi.waitFor(() => expect(wrapper.find('[role="alert"]').exists()).toBe(true), { timeout: 5000 })
  })
})

describe('admin kullanıcı detayı', () => {
  it('profili ve kullanıcının başvurularını gösterir', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/users/12'))

    await vi.waitFor(() => expect(wrapper.find('#user-name').exists()).toBe(true), { timeout: 5000 })
    await waitForRows(wrapper, 2)

    expect(wrapper.get('#user-name').text()).toBe('Ayşe Yılmaz')
    expect(wrapper.text()).toContain('ayse@example.com')
    expect(wrapper.text()).toContain('05553334455')
    expect(wrapper.text()).toContain('Açık hesap')
    expect(wrapper.get('tbody').text()).toContain('Yaşlı 5')
  })

  it('başvuruları applicant süzgeci ve en yeni sıralamasıyla ister', async () => {
    const calls = session()
    ;({ wrapper } = await mountApp('/admin/users/12'))
    await waitForRows(wrapper)

    expect(callsTo(calls, 'get', '/admin/requests/')[0].params).toEqual({ page: 1, ordering: '-created_at', applicant: '12' })
    expect(callsTo(calls, 'get', '/admin/users/12/')).toHaveLength(1)
  })

  it('başvuru satırına tıklayınca başvuru detayına gider', async () => {
    session()
    const mounted = await mountApp('/admin/users/12')
    wrapper = mounted.wrapper
    await waitForRows(wrapper, 2)

    await wrapper.findAll('tbody tr')[0].trigger('click')

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/admin/requests/5'), { timeout: 5000 })
  })

  it('başvurusu olmayan kullanıcıda boş durum metnini gösterir', async () => {
    session({ 'GET /admin/requests/': () => [200, paged([])] })
    ;({ wrapper } = await mountApp('/admin/users/12'))

    await vi.waitFor(() => expect(wrapper.text()).toContain('Bu kullanıcının başvurusu yok.'), { timeout: 5000 })
  })

  it('olmayan kullanıcıda "Bu kullanıcı bulunamadı." uyarısı gösterir', async () => {
    session({ 'GET /admin/users/99/': () => [404, { detail: 'Not found.' }] })
    ;({ wrapper } = await mountApp('/admin/users/99'))

    await vi.waitFor(() => expect(wrapper.text()).toContain('Bu kullanıcı bulunamadı.'), { timeout: 5000 })
    expect(wrapper.find('#user-name').exists()).toBe(false)
  })

  it('kullanıcılara dönüş bağlantısı vardır', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/users/12'))

    await vi.waitFor(() => expect(wrapper.find('a[href="/admin/users"]').exists()).toBe(true), { timeout: 5000 })
  })
})
