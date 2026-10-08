import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { axeViolations } from '../helpers/axe'
import { dashboardResponse } from '../helpers/dashboard'
import { ADMIN, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

// Chart.js jsdom'da çizemez; grafik yerine boş bir canvas bırakılır (veri tablosu ayrıca denetlenir).
vi.mock('primevue/chart', async () => {
  const { h } = await import('vue')
  return { default: { name: 'Chart', props: ['type', 'data', 'options'], setup: () => () => h('canvas') } }
})

let wrapper

afterEach(() => {
  wrapper?.unmount()
  restoreApi()
  window.localStorage.clear()
})

describe('admin kabuğu erişilebilirliği', () => {
  it('admin girişi boş ve hatalı haliyle axe ihlali içermez', async () => {
    ;({ wrapper } = await mountApp('/admin/login'))
    expect(await axeViolations(wrapper.element)).toEqual([])

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('admin yerleşimi axe ihlali içermez', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, ADMIN] }))
    ;({ wrapper } = await mountApp('/admin/dashboard'))

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('veriyle dolu gösterge paneli axe ihlali içermez', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, ADMIN],
      'GET /admin/dashboard/': () => [200, dashboardResponse()],
    }))
    ;({ wrapper } = await mountApp('/admin/dashboard'))
    await vi.waitFor(() => expect(wrapper.find('.pending tbody tr').exists()).toBe(true), { timeout: 5000 })

    expect(await axeViolations(wrapper.element)).toEqual([])
  })
})
