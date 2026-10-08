import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'
import { makeRequest, page } from '../helpers/requests'

let wrapper

/**
 * Oturum açmış başvuru sahibiyle sahte API kurar.
 *
 * @param {Record<string, Function>} routes Ek uç noktalar.
 * @returns {Array<object>} İstek kaydı.
 */
function signedIn(routes) {
  return useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, APPLICANT], ...routes }))
}

beforeEach(() => tokenStorage.set({ access: 'a1', refresh: 'r1' }))
afterEach(() => wrapper?.unmount())

describe('başvurularım sayfası', () => {
  it('başvuruları hizmet, yaşlı, tarih ve durumla listeler', async () => {
    signedIn({ 'GET /requests/': () => [200, page([makeRequest(), makeRequest({ id: 22, status: 'completed', elder_full_name: 'Ahmet Yılmaz' })])] })

    ;({ wrapper } = await mountApp('/requests'))

    const items = wrapper.findAll('.request-item')
    expect(items).toHaveLength(2)
    expect(items[0].text()).toContain('Refakat ve sohbet')
    expect(items[0].text()).toContain('Fatma Yılmaz için')
    expect(items[0].text()).toContain('10 Ekim 2026')
    expect(items[0].text()).toContain('Alındı')
    expect(items[1].text()).toContain('Tamamlandı')
    expect(items[1].attributes('href')).toBe('/requests/22')
  })

  it('başvuru yoksa başvuruya davet eder', async () => {
    signedIn({ 'GET /requests/': () => [200, page([])] })

    ;({ wrapper } = await mountApp('/requests'))

    expect(wrapper.text()).toContain('Henüz bir başvurunuz yok')
    expect(wrapper.get('.requests__cta').attributes('href')).toBe('/requests/new')
  })

  it('daha fazla göster ile sonraki sayfayı ekler', async () => {
    const calls = signedIn({
      'GET /requests/': (config) => (config.params.page === 1
        ? [200, page([makeRequest()], '/api/requests/?page=2')]
        : [200, page([makeRequest({ id: 30 })])]),
    })
    ;({ wrapper } = await mountApp('/requests'))

    await wrapper.findAll('button').find((button) => button.text() === 'Daha fazla göster').trigger('click')
    await flushPromises()

    expect(wrapper.findAll('.request-item')).toHaveLength(2)
    expect(calls.filter((call) => call.url === '/requests/').map((call) => call.params.page)).toEqual([1, 2])
    expect(wrapper.text()).not.toContain('Daha fazla göster')
  })

  it('yüklenemezse tekrar denemeyi sunar', async () => {
    let attempts = 0
    signedIn({ 'GET /requests/': () => { attempts += 1; return attempts === 1 ? [500, {}] : [200, page([makeRequest()])] } })
    ;({ wrapper } = await mountApp('/requests'))

    expect(wrapper.get('[role="alert"]').text()).toContain('yüklenemedi')
    await wrapper.get('.link-button').trigger('click')
    await flushPromises()

    expect(wrapper.findAll('.request-item')).toHaveLength(1)
  })
})

describe('başvuru detay sayfası', () => {
  it('başvuru bilgilerini ve durum çizelgesini gösterir', async () => {
    signedIn({ 'GET /requests/21/': () => [200, makeRequest({ status: 'reviewing' })] })

    ;({ wrapper } = await mountApp('/requests/21'))

    expect(wrapper.get('h1').text()).toBe('Refakat ve sohbet')
    expect(wrapper.text()).toContain('Fatma Yılmaz, 78 yaşında')
    expect(wrapper.text()).toContain('Caferağa Mahallesi, Kadıköy')
    expect(wrapper.text()).toContain('Örnek Mah. No: 1')
    expect(wrapper.get('[aria-current="step"]').text()).toContain('İnceleniyor')
    expect(wrapper.find('.request-detail__success').exists()).toBe(false)
  })

  it('konumu olmayan eski başvuruda mahalle satırında "Yok" gösterir ve adresi ayrı tutar', async () => {
    signedIn({ 'GET /requests/21/': () => [200, makeRequest({ location: null })] })

    ;({ wrapper } = await mountApp('/requests/21'))

    const rows = wrapper.findAll('dt').map((term) => term.text())
    const location = wrapper.findAll('dd')[rows.indexOf('Mahalle ve ilçe')]
    expect(location.text()).toBe('Yok')
    expect(wrapper.text()).toContain('Örnek Mah. No: 1')
  })

  it('sihirbazdan gelindiyse başvurunun alındığını ve aranacağı numarayı söyler', async () => {
    signedIn({ 'GET /requests/21/': () => [200, makeRequest()] })

    ;({ wrapper } = await mountApp('/requests/21?created=1'))

    const success = wrapper.get('.request-detail__success')
    expect(success.attributes('role')).toBe('status')
    expect(success.text()).toContain('Başvurunuz alındı')
    expect(success.text()).toContain('05551112233')
  })

  it('iptal edilen başvuruda yeniden başvurabileceğini açıklar', async () => {
    signedIn({ 'GET /requests/21/': () => [200, makeRequest({ status: 'cancelled' })] })

    ;({ wrapper } = await mountApp('/requests/21'))

    expect(wrapper.text()).toContain('Bu başvuru iptal edildi')
    expect(wrapper.find('.status-timeline').exists()).toBe(false)
  })

  it('bulunamayan başvuruda açıklama gösterir', async () => {
    signedIn({ 'GET /requests/99/': () => [404, { detail: 'Not found.' }] })

    ;({ wrapper } = await mountApp('/requests/99'))

    expect(wrapper.get('h1').text()).toBe('Bu başvuru bulunamadı')
  })
})
