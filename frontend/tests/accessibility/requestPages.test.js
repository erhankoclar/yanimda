import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { axeViolations } from '../helpers/axe'
import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'
import { makeRequest, page } from '../helpers/requests'

let wrapper

beforeEach(() => {
  tokenStorage.set({ access: 'a1', refresh: 'r1' })
  useFakeApi(routeHandler({
    'GET /auth/me/': () => [200, APPLICANT],
    'GET /requests/': () => [200, page([makeRequest(), makeRequest({ id: 22, status: 'cancelled' })])],
    'GET /requests/21/': () => [200, makeRequest({ status: 'assigned' })],
  }))
})
afterEach(() => wrapper?.unmount())

describe('başvuru sayfaları erişilebilirliği', () => {
  it.each(['/requests', '/requests/21', '/requests/21?created=1'])('%s axe ihlali içermez', async (path) => {
    ;({ wrapper } = await mountApp(path))

    expect(await axeViolations(wrapper.element)).toEqual([])
  })
})
