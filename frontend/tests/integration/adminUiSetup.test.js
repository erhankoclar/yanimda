import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

describe('admin arayüzü kurulumu', () => {
  it('son kullanıcı sayfalarında PrimeVue kurulmaz', async () => {
    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.vm.$primevue).toBeUndefined()
  })

  it('admin sayfasına girilince PrimeVue Türkçe yerelleştirmeyle kurulur', async () => {
    ;({ wrapper } = await mountApp('/admin/login'))

    expect(wrapper.vm.$primevue).toBeDefined()
    expect(wrapper.vm.$primevue.config.locale.monthNames[0]).toBe('Ocak')
    expect(wrapper.vm.$toast).toBeDefined()
  })

  it('dil bayrağı İngilizceye geçince PrimeVue metinleri de İngilizce olur', async () => {
    ;({ wrapper } = await mountApp('/admin/login'))

    await wrapper.findAll('.preference-controls__flag')[1].trigger('click')
    await flushPromises()

    expect(wrapper.vm.$primevue.config.locale.monthNames[0]).toBe('January')
  })
})
