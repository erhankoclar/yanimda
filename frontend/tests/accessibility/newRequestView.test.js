import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'
import { isoDateAfter } from '@/utils/dates'

import { axeViolations } from '../helpers/axe'
import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

const FORM = {
  service: 3, elder_full_name: 'Fatma Yılmaz', elder_age: '78', relationship: 'parent',
  preferred_date: isoDateAfter(3), time_slot: 'morning', city: 'Samsun', district: 'İlkadım',
  address: 'No: 1', contact_phone: '05551112233',
}

let wrapper

afterEach(() => {
  wrapper?.unmount()
  window.sessionStorage.clear()
})

describe('başvuru sihirbazı erişilebilirliği', () => {
  it.each([0, 1, 2, 3, 4])('%i. adım boş ve hatalı haliyle axe ihlali içermez', async (step) => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, APPLICANT],
      'GET /services/': () => [200, [{ id: 3, name: 'Refakat', slug: 'r', description: 'd', icon: 'companion' }]],
    }))
    window.sessionStorage.setItem('yanimda.requestDraft', JSON.stringify({ step, form: step === 4 ? FORM : {} }))
    ;({ wrapper } = await mountApp('/requests/new'))
    expect(await axeViolations(wrapper.element)).toEqual([])

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('adım geçişinde odak yeni adımın başlığına taşınır', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, APPLICANT],
      'GET /services/': () => [200, [{ id: 3, name: 'Refakat', slug: 'r', description: 'd', icon: 'companion' }]],
    }))
    ;({ wrapper } = await mountApp('/requests/new?service=3'))

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(document.activeElement).toBe(wrapper.get('h1').element)
    expect(document.activeElement.textContent).toBe('Destek kimin için?')
  })
})
