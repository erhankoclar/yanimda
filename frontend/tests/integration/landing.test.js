import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

const SERVICES = [
  { id: 3, name: 'Refakat ve sohbet', slug: 'refakat', description: 'Düzenli ziyaret', icon: 'companion' },
  { id: 4, name: 'Hastane eşliği', slug: 'hastane', description: 'Randevulara eşlik', icon: 'hospital' },
]

let wrapper

afterEach(() => wrapper?.unmount())

describe('ana sayfa', () => {
  it('hizmetleri API’den listeler ve her birini o hizmetle başvuruya bağlar', async () => {
    useFakeApi(routeHandler({ 'GET /services/': () => [200, SERVICES] }))

    ;({ wrapper } = await mountApp('/'))

    const items = wrapper.findAll('.service-overview__item')
    expect(items.map((item) => item.text())).toEqual([
      expect.stringContaining('Refakat ve sohbet'),
      expect.stringContaining('Hastane eşliği'),
    ])
    expect(items[1].attributes('href')).toBe('/requests/new?service=4')
  })

  it('hizmetler yüklenemezse açıklama ve tekrar deneme düğmesi gösterir', async () => {
    let attempts = 0
    useFakeApi(routeHandler({
      'GET /services/': () => {
        attempts += 1
        return attempts === 1 ? [500, {}] : [200, SERVICES]
      },
    }))
    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.get('[role="alert"]').text()).toContain('yüklenemedi')
    await wrapper.get('.service-overview__retry').trigger('click')
    await flushPromises()

    expect(wrapper.findAll('.service-overview__item')).toHaveLength(2)
  })

  it('başvuru çağrısı başvuru sayfasına gider', async () => {
    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.get('.landing__cta').attributes('href')).toBe('/requests/new')
    expect(wrapper.find('.landing__secondary').exists()).toBe(false)
  })

  it('oturumu açık kullanıcıya başvurularına giden bağlantıyı da gösterir', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, APPLICANT], 'GET /services/': () => [200, []] }))

    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.get('.landing__secondary').attributes('href')).toBe('/requests')
  })

  it('oturumsuz kullanıcı başvuruya başlayınca girişe yönlendirilir', async () => {
    const mounted = await mountApp('/')
    wrapper = mounted.wrapper

    await wrapper.get('.landing__cta').trigger('click')
    await flushPromises()

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.name).toBe('login'))
    expect(mounted.router.currentRoute.value.query.redirect).toBe('/requests/new')
  })
})

describe('ana sayfa bölümleri', () => {
  it('menüdeki bölüm bağlantılarının hedeflerini içerir', async () => {
    ;({ wrapper } = await mountApp('/'))

    ;['hizmetler', 'nasil-isler', 'sss'].forEach((id) => expect(wrapper.find(`#${id}`).exists(), id).toBe(true))
  })

  it('sık sorulanları açılır kapanır biçimde listeler', async () => {
    ;({ wrapper } = await mountApp('/'))

    const items = wrapper.findAll('#sss details')
    expect(items.length).toBeGreaterThanOrEqual(5)
    expect(items.every((item) => item.find('summary').text().endsWith('?'))).toBe(true)
  })

  it('tüm fotoğraflar açıklayıcı alternatif metin taşır', async () => {
    ;({ wrapper } = await mountApp('/'))

    const images = wrapper.findAll('img')
    expect(images.length).toBe(3)
    images.forEach((image) => expect(image.attributes('alt').length).toBeGreaterThan(20))
  })
})
