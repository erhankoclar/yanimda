import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { axeViolations } from '../helpers/axe'
import { ADMIN, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

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
})
