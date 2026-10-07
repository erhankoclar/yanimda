import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => {
  wrapper?.unmount()
  window.sessionStorage.clear()
})

describe('başvuru taslağı güvenliği', () => {
  it('çıkış yapınca kişisel bilgi içeren taslağı siler', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, APPLICANT], 'GET /services/': () => [200, []] }))
    window.sessionStorage.setItem('yanimda.requestDraft', JSON.stringify({
      step: 2, form: { elder_full_name: 'Fatma Yılmaz', address: 'Örnek Mah. No: 1' },
    }))
    ;({ wrapper } = await mountApp('/requests/new'))

    await wrapper.get('nav button').trigger('click')
    await flushPromises()

    expect(window.sessionStorage.getItem('yanimda.requestDraft') ?? '').not.toContain('Fatma')
  })

  it('taslak kalıcı depoya (localStorage) yazılmaz', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, APPLICANT], 'GET /services/': () => [200, []] }))
    ;({ wrapper } = await mountApp('/requests/new?service=3'))

    const keys = Object.keys(window.localStorage)
    expect(keys.some((key) => key.includes('Draft'))).toBe(false)
  })
})
