import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

/**
 * Üst çubuktaki bayrak düğmesine basar ve ekranın yenilenmesini bekler.
 *
 * @param {number} index 0: Türkçe, 1: İngilizce.
 */
async function pickLanguage(index) {
  await wrapper.findAll('.preference-controls__flag')[index].trigger('click')
  await flushPromises()
}

describe('dil değişimi', () => {
  it('İngilizce bayrağı ana sayfadaki başlığı, gezinmeyi ve talep düğmesini anında çevirir', async () => {
    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.find('h1').text()).toBe('Annenizin, babanızın yanında olalım.')

    await pickLanguage(1)

    expect(wrapper.find('h1').text()).toBe('Let us be there for your mum and dad.')
    const navigation = wrapper.find('.site-header__sections').text()
    expect(navigation).toContain('Services')
    expect(navigation).toContain('How it works')
    expect(navigation).toContain('FAQ')
    expect(wrapper.find('#talep-formu button[type="submit"]').text()).toBe('Send my request')
  })

  it('Türkçe bayrağına dönünce metinlerin hepsi Türkçe olarak geri gelir', async () => {
    ;({ wrapper } = await mountApp('/'))

    await pickLanguage(1)
    await pickLanguage(0)

    expect(wrapper.find('h1').text()).toBe('Annenizin, babanızın yanında olalım.')
    const navigation = wrapper.find('.site-header__sections').text()
    expect(navigation).toContain('Hizmetler')
    expect(navigation).toContain('Nasıl işler?')
    expect(navigation).toContain('Sık sorulanlar')
    expect(wrapper.find('#talep-formu button[type="submit"]').text()).toBe('Talebimi gönder')
  })

  it('SSS soruları gibi betikteki listelerden üretilen metinler de dil değişince güncellenir', async () => {
    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.find('.faq__item summary').text()).toBe('Başvuru için neler gerekiyor?')

    await pickLanguage(1)

    expect(wrapper.find('.faq__item summary').text()).toBe('What do I need to make a request?')
  })
})
