import { afterEach, describe, expect, it } from 'vitest'

import { axeViolations } from '../helpers/axe'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

describe('PublicLayout erişilebilirliği', () => {
  it('axe ihlali içermez', async () => {
    ;({ wrapper } = await mountApp('/'))

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('ilk odaklanabilir öğe ana içeriğe atlama bağlantısıdır', async () => {
    ;({ wrapper } = await mountApp('/'))

    const first = wrapper.element.querySelector('a, button')
    expect(first.getAttribute('href')).toBe('#main-content')
    expect(wrapper.find('#main-content').exists()).toBe(true)
  })

  it('tek bir main ve tek bir h1 bölgesi vardır', async () => {
    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.findAll('main')).toHaveLength(1)
    expect(wrapper.findAll('h1')).toHaveLength(1)
  })
})
