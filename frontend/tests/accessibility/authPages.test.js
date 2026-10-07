import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { axeViolations } from '../helpers/axe'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

describe('giriş ve kayıt sayfaları erişilebilirliği', () => {
  it.each(['/login', '/register'])('%s boş ve hatalı haliyle axe ihlali içermez', async (path) => {
    ;({ wrapper } = await mountApp(path))
    expect(await axeViolations(wrapper.element)).toEqual([])

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(await axeViolations(wrapper.element)).toEqual([])
  })
})
