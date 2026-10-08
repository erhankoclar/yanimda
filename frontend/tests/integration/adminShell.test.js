import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { ADMIN, APPLICANT, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => {
  wrapper?.unmount()
  restoreApi()
  window.localStorage.clear()
})

/**
 * Admin giriş formunu doldurup gönderir.
 *
 * @param {string} email E-posta.
 * @param {string} password Parola.
 */
async function signIn(email, password) {
  await wrapper.get('#admin-email').setValue(email)
  await wrapper.get('#admin-password').setValue(password)
  await wrapper.get('form').trigger('submit')
  await flushPromises()
}

/**
 * Giriş uç noktası verilen kullanıcıyı döndüren sahte API kurar.
 *
 * @param {object} user `/auth/me/` yanıtı.
 * @returns {Array<object>} İstek kaydı.
 */
function loginReturns(user) {
  return useFakeApi(routeHandler({
    'POST /auth/token/': () => [200, { access: 'a1', refresh: 'r1' }],
    'GET /auth/me/': () => [200, user],
    'POST /auth/logout/': () => [205, {}],
  }))
}

/** Admin olarak oturum açılmış gibi token ve sahte API hazırlar. */
function signedInAsAdmin() {
  tokenStorage.set({ access: 'a1', refresh: 'r1' })
  return useFakeApi(routeHandler({
    'GET /auth/me/': () => [200, ADMIN],
    'POST /auth/logout/': () => [205, {}],
  }))
}

describe('admin girişi', () => {
  it('boş gönderimde alan hatalarını gösterir ve istek yapmaz', async () => {
    const calls = useFakeApi(() => [200, {}])
    ;({ wrapper } = await mountApp('/admin/login'))

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.get('#admin-email-error').text()).toBe('E-posta adresinizi yazın.')
    expect(wrapper.get('#admin-password-error').text()).toBe('Parolanızı yazın.')
    expect(calls.filter((call) => call.url === '/auth/token/')).toHaveLength(0)
  })

  it('yönetici hesabıyla girişte gösterge paneline gider', async () => {
    loginReturns(ADMIN)
    const mounted = await mountApp('/admin/login')
    wrapper = mounted.wrapper

    await signIn('admin@example.com', 'Kurgusal-Parola-1')

    // Admin sayfaları tembel yüklendiği için yönlendirmenin bitmesi beklenir.
    await vi.waitFor(() => expect(mounted.router.currentRoute.value.name).toBe('admin-dashboard'), { timeout: 5000 })
    expect(wrapper.find('[data-layout="admin"]').exists()).toBe(true)
  })

  it('yönetici, girişten sonra geldiği admin sayfasına döner', async () => {
    loginReturns(ADMIN)
    const mounted = await mountApp('/admin/requests')
    wrapper = mounted.wrapper
    expect(mounted.router.currentRoute.value.name).toBe('admin-login')

    await signIn('admin@example.com', 'Kurgusal-Parola-1')

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.name).toBe('admin-requests'), { timeout: 5000 })
  })

  it('başvuru sahibi hesabıyla girişte uyarı gösterir ve oturumu hemen kapatır', async () => {
    const calls = loginReturns(APPLICANT)
    const mounted = await mountApp('/admin/login')
    wrapper = mounted.wrapper

    await signIn('ayse@example.com', 'Kurgusal-Parola-1')

    expect(mounted.router.currentRoute.value.name).toBe('admin-login')
    expect(wrapper.get('[role="alert"]').text()).toContain('yönetim paneline erişim yetkisi yok')
    expect(tokenStorage.getAccess()).toBeNull()
    expect(calls.some((call) => call.url === '/auth/logout/')).toBe(true)
  })

  it('hatalı bilgilerde genel hata gösterir', async () => {
    useFakeApi(routeHandler({ 'POST /auth/token/': () => [401, { detail: 'No active account' }] }))
    ;({ wrapper } = await mountApp('/admin/login'))

    await signIn('admin@example.com', 'yanlis')

    expect(wrapper.get('[role="alert"]').text()).toContain('E-posta adresi veya parola hatalı.')
  })
})

describe('admin yerleşimi', () => {
  it('üst barda sayfanın başlığını tek h1 olarak gösterir', async () => {
    signedInAsAdmin()
    ;({ wrapper } = await mountApp('/admin/users'))

    const headings = wrapper.findAll('h1')
    expect(headings).toHaveLength(1)
    expect(headings[0].text()).toBe('Kullanıcılar')
  })

  it('menüde beş bölümü listeler ve detay sayfasında kendi bölümünü etkin gösterir', async () => {
    signedInAsAdmin()
    ;({ wrapper } = await mountApp('/admin/requests/7'))

    const sidebar = wrapper.get('.admin-layout__sidebar')
    const links = sidebar.findAll('.admin-nav__link')
    expect(links.map((link) => link.text())).toEqual(['Gösterge paneli', 'Hızlı talepler', 'Başvurular', 'Talep haritası', 'Kullanıcılar'])
    const active = sidebar.findAll('.admin-nav__link.is-active')
    expect(active).toHaveLength(1)
    expect(active[0].text()).toBe('Başvurular')
    expect(active[0].attributes('aria-current')).toBe('page')
  })

  it('oturumdaki yöneticinin adını gösterir', async () => {
    signedInAsAdmin()
    ;({ wrapper } = await mountApp('/admin/dashboard'))

    expect(wrapper.get('.admin-layout__user').text()).toBe(ADMIN.first_name)
  })

  it('çıkış düğmesi oturumu kapatır ve admin girişine döner', async () => {
    const calls = signedInAsAdmin()
    const mounted = await mountApp('/admin/dashboard')
    wrapper = mounted.wrapper

    await wrapper.get('.admin-layout__logout').trigger('click')
    await flushPromises()

    expect(mounted.router.currentRoute.value.name).toBe('admin-login')
    expect(tokenStorage.getRefresh()).toBeNull()
    expect(calls.some((call) => call.url === '/auth/logout/')).toBe(true)
  })

  it('dil İngilizceye geçince başlık ve menü İngilizce olur', async () => {
    signedInAsAdmin()
    ;({ wrapper } = await mountApp('/admin/inquiries'))

    await wrapper.findAll('.preference-controls__flag')[1].trigger('click')
    await flushPromises()

    expect(wrapper.get('h1').text()).toBe('Quick inquiries')
    expect(wrapper.get('.admin-layout__sidebar').text()).toContain('Applications')
  })
})
