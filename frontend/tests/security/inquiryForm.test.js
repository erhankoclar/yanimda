import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

describe('hızlı talep formu güvenliği', () => {
  it('spam tuzağı alanı ekran okuyuculardan ve klavyeden gizlidir', async () => {
    ;({ wrapper } = await mountApp('/'))

    const trap = wrapper.get('#inquiry-website')
    expect(trap.attributes('tabindex')).toBe('-1')
    expect(trap.element.closest('[aria-hidden="true"]')).not.toBeNull()
  })

  it('oturum açıkken talep 401 alsa bile token yenileme döngüsüne girmez ve başarı göstermez', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    const calls = useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, { id: 1, email: 'a@example.com', is_staff: false }],
      'GET /services/': () => [200, [{ id: 3, name: 'Refakat', slug: 'r', description: 'd', icon: 'companion' }]],
      'POST /inquiries/': () => [401, {}],
    }))
    ;({ wrapper } = await mountApp('/'))
    const section = wrapper.get('#talep-formu')
    const inputs = section.findAll('input')
    await inputs.find((input) => input.attributes('autocomplete') === 'name').setValue('Deneme Kişi')
    await inputs.find((input) => input.attributes('type') === 'email').setValue('deneme@example.com')
    await section.get('select').setValue(3)
    await section.findAll('select')[1].setValue(5)
    await flushPromises()
    await section.findAll('select')[2].setValue(11)
    await section.get('textarea').setValue('Annem için refakat desteği istiyoruz.')
    await section.get('input[type="checkbox"]').setValue(true)

    await section.get('form').trigger('submit')
    await flushPromises()

    const inquiry = calls.find((call) => call.url === '/inquiries/')
    expect(inquiry).toBeDefined()
    expect(inquiry.headers.Authorization).toBeDefined()
    expect(calls.some((call) => call.url === '/auth/token/refresh/')).toBe(false)
    expect(wrapper.find('.inquiry__success').exists()).toBe(false)
  })
})
