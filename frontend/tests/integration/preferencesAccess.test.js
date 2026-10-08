import { afterEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { ADMIN, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

afterEach(() => restoreApi())

describe('dil ve tema seçimi her yerden erişilebilir', () => {
  it.each(['/', '/login', '/register', '/admin/login'])('%s sayfasında bayraklar ve tema düğmesi görünür', async (path) => {
    const { wrapper } = await mountApp(path)

    expect(wrapper.findAll('.preference-controls__flag')).toHaveLength(2)
    expect(wrapper.find('.preference-controls__theme').exists()).toBe(true)
    wrapper.unmount()
  })

  it('admin panelinin üst çubuğunda bayraklar ve tema düğmesi görünür', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, ADMIN] }))
    const { wrapper } = await mountApp('/admin/dashboard')

    expect(wrapper.find('.admin-layout__topbar .preference-controls').exists()).toBe(true)
    wrapper.unmount()
  })

  it('dil seçimi sayfa değişince korunur', async () => {
    const { wrapper, router } = await mountApp('/')
    await wrapper.findAll('.preference-controls__flag')[1].trigger('click')

    await router.push('/login')

    expect(document.documentElement.lang).toBe('en')
    expect(wrapper.findAll('.preference-controls__flag')[1].attributes('aria-pressed')).toBe('true')
    wrapper.unmount()
  })
})
