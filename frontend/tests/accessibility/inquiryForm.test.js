import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { axeViolations } from '../helpers/axe'
import { routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

describe('hızlı talep formu erişilebilirliği', () => {
  it('boş, hatalı ve başarılı halleriyle axe ihlali içermez; başarıda odak mesaja taşınır', async () => {
    useFakeApi(routeHandler({
      'GET /services/': () => [200, [{ id: 3, name: 'Refakat', slug: 'r', description: 'd', icon: 'companion' }]],
      'POST /inquiries/': () => [201, { id: 9 }],
    }))
    ;({ wrapper } = await mountApp('/'))
    const section = () => wrapper.get('#talep-formu')
    expect(await axeViolations(section().element)).toEqual([])

    await section().get('form').trigger('submit')
    await flushPromises()
    expect(await axeViolations(section().element)).toEqual([])

    const inputs = section().findAll('input')
    await inputs.find((input) => input.attributes('autocomplete') === 'name').setValue('Deneme Kişi')
    await inputs.find((input) => input.attributes('type') === 'email').setValue('deneme@example.com')
    await section().get('select').setValue(3)
    await section().findAll('select')[1].setValue(5)
    await flushPromises()
    await section().findAll('select')[2].setValue(11)
    await section().get('textarea').setValue('Annem için refakat desteği istiyoruz.')
    await section().get('input[type="checkbox"]').setValue(true)
    await section().get('form').trigger('submit')
    await flushPromises()

    expect(document.activeElement).toBe(wrapper.get('.inquiry__success').element)
    expect(await axeViolations(section().element)).toEqual([])
  })
})
