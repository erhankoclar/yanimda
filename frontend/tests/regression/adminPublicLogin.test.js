import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { ADMIN, APPLICANT, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

// Admin sayfaları tembel yüklenir; ilk yükleme yoğun makinede yavaş olabildiği için önceden ısıtılır.
beforeAll(async () => {
  await import('@/views/admin/DashboardView.vue')
}, 90000)

afterEach(() => {
  wrapper?.unmount()
  restoreApi()
  window.localStorage.clear()
})

/**
 * Genel giriş sayfasındaki formu doldurup gönderir.
 *
 * @param {import('@vue/test-utils').VueWrapper} app Bağlanmış uygulama.
 */
async function submitPublicLogin(app) {
  const inputs = app.findAll('input')
  await inputs[0].setValue('kullanici@example.com')
  await inputs[1].setValue('Kurgusal-Parola-1')
  await app.get('form').trigger('submit')
  await flushPromises()
}

/**
 * Giriş uç noktası verilen kullanıcıyı döndüren sahte API kurar.
 *
 * @param {object} user `/auth/me/` yanıtı.
 */
function loginReturns(user) {
  useFakeApi(routeHandler({
    'POST /auth/token/': () => [200, { access: 'a1', refresh: 'r1' }],
    'GET /auth/me/': () => [200, user],
    'POST /auth/logout/': () => [205, {}],
  }))
}

/**
 * Verilen kullanıcıyla oturum açılmış gibi token ve sahte API hazırlar.
 *
 * @param {object} user Oturumdaki kullanıcı.
 */
function signedInAs(user) {
  tokenStorage.set({ access: 'a1', refresh: 'r1' })
  useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, user], 'POST /auth/logout/': () => [205, {}] }))
}

describe('genel giriş sayfasından yönetici girişi', () => {
  it('yönetici, yönlendirme adresi yokken gösterge paneline gider', async () => {
    loginReturns(ADMIN)
    const mounted = await mountApp('/login')
    wrapper = mounted.wrapper

    await submitPublicLogin(wrapper)

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/admin/dashboard'), { timeout: 5000 })
  })

  it('başvuru sahibi, yönlendirme adresi yokken başvurularına gider', async () => {
    loginReturns(APPLICANT)
    const mounted = await mountApp('/login')
    wrapper = mounted.wrapper

    await submitPublicLogin(wrapper)

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/requests'), { timeout: 5000 })
  })

  it('güvenli bir yönlendirme adresi yönetici için de önceliklidir', async () => {
    loginReturns(ADMIN)
    const mounted = await mountApp(`/login?redirect=${encodeURIComponent('/requests/new')}`)
    wrapper = mounted.wrapper

    await submitPublicLogin(wrapper)

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/requests/new'), { timeout: 5000 })
  })

  it.each(['//evil.com', 'https://evil.com/x'])(
    'güvensiz yönlendirme adresini (%s) yok sayıp yöneticiyi gösterge paneline götürür',
    async (target) => {
      loginReturns(ADMIN)
      const mounted = await mountApp(`/login?redirect=${encodeURIComponent(target)}`)
      wrapper = mounted.wrapper

      await submitPublicLogin(wrapper)

      await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/admin/dashboard'), { timeout: 5000 })
    },
  )
})

describe('guestOnly route’ları ve oturumlu kullanıcı', () => {
  it.each(['/login', '/register'])('oturumlu yönetici %s sayfasını açınca gösterge paneline yönlenir', async (path) => {
    signedInAs(ADMIN)

    const mounted = await mountApp(path)
    wrapper = mounted.wrapper

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.name).toBe('admin-dashboard'), { timeout: 5000 })
  })

  it.each(['/login', '/register'])('oturumlu başvuru sahibi %s sayfasını açınca başvurularına yönlenir', async (path) => {
    signedInAs(APPLICANT)

    const mounted = await mountApp(path)
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('request-list')
  })

  it('oturumsuz kullanıcı genel giriş sayfasını görür', async () => {
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [401, {}] }))

    const mounted = await mountApp('/login')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('login')
  })
})

describe('site başlığındaki yönetim paneli bağlantısı', () => {
  it('yöneticiye Yönetim paneli bağlantısını gösterir ve gösterge paneline bağlar', async () => {
    signedInAs(ADMIN)
    ;({ wrapper } = await mountApp('/'))

    const link = wrapper.get('nav[aria-label="Hesap"]').findAll('a').find((item) => item.text() === 'Yönetim paneli')

    expect(link).toBeDefined()
    expect(link.attributes('href')).toBe('/admin/dashboard')
  })

  it('başvuru sahibine yönetim paneli bağlantısını göstermez', async () => {
    signedInAs(APPLICANT)
    ;({ wrapper } = await mountApp('/'))

    const nav = wrapper.get('nav[aria-label="Hesap"]')

    expect(nav.text()).toContain('Başvurularım')
    expect(nav.text()).not.toContain('Yönetim paneli')
  })

  it('oturumsuz ziyaretçiye yönetim paneli bağlantısını göstermez', async () => {
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [401, {}] }))
    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.get('nav[aria-label="Hesap"]').text()).not.toContain('Yönetim paneli')
  })

  it('İngilizce arayüzde bağlantı Admin panel olur', async () => {
    signedInAs(ADMIN)
    ;({ wrapper } = await mountApp('/'))

    await wrapper.findAll('.preference-controls__flag')[1].trigger('click')
    await flushPromises()

    expect(wrapper.get('nav[aria-label="Account"]').text()).toContain('Admin panel')
  })

  it('bağlantıya tıklayınca yönetim paneli açılır', async () => {
    signedInAs(ADMIN)
    const mounted = await mountApp('/')
    wrapper = mounted.wrapper

    const link = wrapper.get('nav[aria-label="Hesap"]').findAll('a').find((item) => item.text() === 'Yönetim paneli')
    await link.trigger('click')

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.name).toBe('admin-dashboard'), { timeout: 5000 })
  })
})
