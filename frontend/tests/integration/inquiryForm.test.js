import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import { routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

const SERVICES = [
  { id: 3, name: 'Refakat ve sohbet', slug: 'refakat', description: 'd', icon: 'companion' },
  { id: 4, name: 'Hastane eşliği', slug: 'hastane', description: 'd', icon: 'hospital' },
]

let wrapper

/**
 * Talep formu bölümündeki etiketiyle bulunan alana değer yazar.
 *
 * @param {string} label Etiket başlangıcı.
 * @param {string} value Değer.
 */
async function fill(label, value) {
  const section = wrapper.get('#talep-formu')
  const labelEl = section.findAll('label').find((item) => item.text().startsWith(label))
  await section.get(`#${labelEl.attributes('for')}`).setValue(value)
}

/** Formu geçerli bilgilerle doldurur. */
async function fillValid() {
  await fill('Adınız ve soyadınız', 'Deneme Kişi')
  await fill('E-posta adresiniz', 'deneme@example.com')
  await wrapper.get('#talep-formu select').setValue(4)
  await fill('Kısaca anlatın', 'Babam için hastane randevusuna eşlik istiyoruz.')
  await wrapper.get('#talep-formu input[type="checkbox"]').setValue(true)
}

const submit = () => wrapper.get('#talep-formu form').trigger('submit')
const successShown = () => wrapper.find('.inquiry__success').exists()

afterEach(() => wrapper?.unmount())

describe('hızlı talep formu', () => {
  it('isim, e-posta, hizmet seçimi ve açıklama alanlarını içerir', async () => {
    useFakeApi(routeHandler({ 'GET /services/': () => [200, SERVICES] }))
    ;({ wrapper } = await mountApp('/'))

    const labels = wrapper.get('#talep-formu').findAll('label').map((label) => label.text())
    ;['Adınız ve soyadınız', 'E-posta adresiniz', 'Hangi hizmet?', 'Kısaca anlatın'].forEach((label) => {
      expect(labels.some((text) => text.startsWith(label)), label).toBe(true)
    })
    expect(wrapper.get('#talep-formu select').findAll('option').map((option) => option.text()))
      .toEqual(['Bir hizmet seçin', 'Refakat ve sohbet', 'Hastane eşliği'])
  })

  it('istemci doğrulaması başarısızsa istek göndermez ve alan hatalarını gösterir', async () => {
    const calls = useFakeApi(routeHandler({ 'GET /services/': () => [200, SERVICES] }))
    ;({ wrapper } = await mountApp('/'))

    await submit()
    await flushPromises()

    expect(calls.filter((call) => call.url === '/inquiries/')).toHaveLength(0)
    expect(wrapper.get('#talep-formu').findAll('[aria-invalid="true"]').length).toBeGreaterThanOrEqual(4)
    expect(successShown()).toBe(false)
  })

  it('gönderilirken "Gönderiliyor…" gösterir, alanları kilitler; başarıyı yalnızca kayıt dönünce gösterir', async () => {
    let release
    const calls = useFakeApi(routeHandler({
      'GET /services/': () => [200, SERVICES],
      'POST /inquiries/': () => new Promise((resolve) => { release = () => resolve([201, { id: 42, created_at: '2026-10-07T10:00:00Z' }]) }),
    }))
    ;({ wrapper } = await mountApp('/'))
    await fillValid()

    await submit()
    await flushPromises()

    const button = wrapper.get('#talep-formu button[type="submit"]')
    expect(button.text()).toBe('Gönderiliyor…')
    expect(button.attributes('disabled')).toBeDefined()
    expect(wrapper.get('#talep-formu fieldset').attributes('disabled')).toBeDefined()
    expect(successShown()).toBe(false)

    release()
    await flushPromises()

    const success = wrapper.get('.inquiry__success')
    expect(success.attributes('role')).toBe('status')
    expect(success.text()).toContain('Talebiniz alındı')
    expect(success.text()).toContain('#42')
    const sent = JSON.parse(calls.find((call) => call.url === '/inquiries/').data)
    expect(sent).toEqual({
      full_name: 'Deneme Kişi', email: 'deneme@example.com', service: 4,
      message: 'Babam için hastane randevusuna eşlik istiyoruz.', consent: true, website: '',
    })
  })

  it.each([
    ['sunucu hatası (500)', () => [500, {}], 'Beklenmeyen bir sorun'],
    ['hız sınırı (429)', () => [429, {}], 'Çok fazla deneme'],
    ['ağ hatası', () => { throw new Error('ağ yok') }, 'Sunucuya ulaşılamadı'],
  ])('%s durumunda başarı göstermez, hata mesajı verir ve yazılanları korur', async (_name, responder, message) => {
    useFakeApi(routeHandler({ 'GET /services/': () => [200, SERVICES], 'POST /inquiries/': responder }))
    ;({ wrapper } = await mountApp('/'))
    await fillValid()

    await submit()
    await flushPromises()

    expect(successShown()).toBe(false)
    expect(wrapper.get('#talep-formu [role="alert"]').text()).toContain(message)
    expect(wrapper.get('#talep-formu textarea').element.value).toContain('hastane randevusuna')
    expect(wrapper.get('#talep-formu button[type="submit"]').text()).toBe('Talebimi gönder')
  })

  it('sunucu doğrulama hatasını ilgili alanın altında gösterir', async () => {
    useFakeApi(routeHandler({
      'GET /services/': () => [200, SERVICES],
      'POST /inquiries/': () => [400, { email: ['Geçerli bir e-posta adresi girin.'] }],
    }))
    ;({ wrapper } = await mountApp('/'))
    await fillValid()

    await submit()
    await flushPromises()

    const email = wrapper.get('#talep-formu input[type="email"]')
    expect(email.attributes('aria-invalid')).toBe('true')
    expect(wrapper.get('#talep-formu').text()).toContain('Geçerli bir e-posta adresi girin.')
    expect(successShown()).toBe(false)
  })

  it('sunucu kayıt numarası döndürmezse başarı göstermez', async () => {
    useFakeApi(routeHandler({ 'GET /services/': () => [200, SERVICES], 'POST /inquiries/': () => [200, {}] }))
    ;({ wrapper } = await mountApp('/'))
    await fillValid()

    await submit()
    await flushPromises()

    expect(successShown()).toBe(false)
  })

  it('hizmet kartından gelince hizmet seçili başlar ve yeni talep formu boşaltır', async () => {
    useFakeApi(routeHandler({
      'GET /services/': () => [200, SERVICES],
      'POST /inquiries/': () => [201, { id: 7 }],
    }))
    ;({ wrapper } = await mountApp('/?service=3'))
    expect(wrapper.get('#talep-formu select').element.value).toBe('3')

    await fillValid()
    await submit()
    await flushPromises()
    await wrapper.findAll('.inquiry__success button').at(0).trigger('click')

    expect(wrapper.get('#talep-formu textarea').element.value).toBe('')
  })
})
