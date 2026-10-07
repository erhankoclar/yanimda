import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { APPLICANT, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => {
  wrapper?.unmount()
  restoreApi()
  window.localStorage.clear()
})

describe('PublicLayout', () => {
  it('oturum yokken yalnızca giriş bağlantısını gösterir', async () => {
    ;({ wrapper } = await mountApp('/'))

    const nav = wrapper.get('nav[aria-label="Hesap"]')
    expect(nav.text()).toContain('Giriş yap')
    expect(nav.text()).not.toContain('Başvurularım')
  })

  it('oturum açıkken başvurular bağlantısını ve çıkış düğmesini gösterir', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, APPLICANT] }))

    ;({ wrapper } = await mountApp('/'))

    const nav = wrapper.get('nav[aria-label="Hesap"]')
    expect(nav.text()).toContain('Başvurularım')
    expect(nav.find('button').text()).toBe('Çıkış yap')
  })

  it('çıkış yapınca oturumu kapatıp ana sayfaya döner', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, APPLICANT] }))
    const mounted = await mountApp('/requests')
    wrapper = mounted.wrapper

    await wrapper.get('nav button').trigger('click')
    await flushPromises()

    expect(mounted.router.currentRoute.value.name).toBe('landing')
    expect(tokenStorage.getAccess()).toBeNull()
    expect(wrapper.get('nav').text()).toContain('Giriş yap')
  })
})
