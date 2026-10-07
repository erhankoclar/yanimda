import { afterEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'
import { makeRequest } from '../helpers/requests'

let wrapper

afterEach(() => wrapper?.unmount())

describe('başvuru detayı güvenliği', () => {
  it('API yanlışlıkla yönetici notu döndürse bile ekranda göstermez', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, APPLICANT],
      'GET /requests/21/': () => [200, makeRequest({ admin_note: 'GIZLI-IC-NOT' })],
    }))

    ;({ wrapper } = await mountApp('/requests/21'))

    expect(wrapper.html()).not.toContain('GIZLI-IC-NOT')
  })

  it('başkasının başvurusu (404) için hiçbir veri göstermez', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, APPLICANT], 'GET /requests/5/': () => [404, {}] }))

    ;({ wrapper } = await mountApp('/requests/5'))

    expect(wrapper.find('.request-detail__list').exists()).toBe(false)
    expect(wrapper.text()).toContain('size ait değil')
  })

  it('başvuru metinlerini HTML olarak yorumlamaz (XSS)', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, APPLICANT],
      'GET /requests/21/': () => [200, makeRequest({ elder_notes: '<img src=x onerror="window.__xss=1">' })],
    }))

    ;({ wrapper } = await mountApp('/requests/21'))

    expect(wrapper.find('img').exists()).toBe(false)
    expect(window.__xss).toBeUndefined()
    expect(wrapper.text()).toContain('<img src=x')
  })
})
