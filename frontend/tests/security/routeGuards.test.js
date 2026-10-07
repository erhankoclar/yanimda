import { afterEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { ADMIN, APPLICANT, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

/**
 * Verilen kullanıcıyla oturum açılmış gibi sahte API ve token hazırlar.
 *
 * @param {object | null} user Oturumdaki kullanıcı; null ise oturum yoktur.
 */
function signedInAs(user) {
  if (user) tokenStorage.set({ access: 'a1', refresh: 'r1' })
  useFakeApi(routeHandler({ 'GET /auth/me/': () => (user ? [200, user] : [401, {}]) }))
}

afterEach(() => {
  wrapper?.unmount()
  restoreApi()
  window.localStorage.clear()
})

describe('route guard’ları', () => {
  it('oturumsuz kullanıcıyı başvuru sayfasından girişe, dönüş adresiyle yönlendirir', async () => {
    signedInAs(null)

    const mounted = await mountApp('/requests/new')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('login')
    expect(mounted.router.currentRoute.value.query.redirect).toBe('/requests/new')
  })

  it('oturumsuz kullanıcıyı admin sayfalarından admin girişine yönlendirir', async () => {
    signedInAs(null)

    const mounted = await mountApp('/admin/requests')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('admin-login')
  })

  it('başvuru sahibinin admin paneline girmesini engeller (yetki yükseltme)', async () => {
    signedInAs(APPLICANT)

    const mounted = await mountApp('/admin/users')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('admin-login')
    expect(wrapper.find('[data-layout="admin"]').exists()).toBe(false)
  })

  it('admin kullanıcı admin sayfalarını açabilir', async () => {
    signedInAs(ADMIN)

    const mounted = await mountApp('/admin/requests')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('admin-requests')
    expect(wrapper.find('[data-layout="admin"]').exists()).toBe(true)
  })

  it('oturumu açık kullanıcıyı giriş sayfasından başvurularına yönlendirir', async () => {
    signedInAs(APPLICANT)

    const mounted = await mountApp('/login')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('request-list')
  })

  it('oturumu açık admini admin girişinden gösterge paneline yönlendirir', async () => {
    signedInAs(ADMIN)

    const mounted = await mountApp('/admin/login')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('admin-dashboard')
  })
})
