import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'
import { isoDateAfter } from '@/utils/dates'

import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

const SERVICES = [
  { id: 3, name: 'Refakat ve sohbet', slug: 'refakat', description: 'Düzenli ziyaret', icon: 'companion' },
  { id: 4, name: 'Hastane eşliği', slug: 'hastane', description: 'Randevulara eşlik', icon: 'hospital' },
]

let wrapper
let calls

/**
 * Oturum açmış başvuru sahibi ve hizmet listesiyle sahte API hazırlar.
 *
 * @param {Record<string, Function>} [extra] Ek sahte uç noktalar.
 */
function signedIn(extra = {}) {
  tokenStorage.set({ access: 'a1', refresh: 'r1' })
  calls = useFakeApi(routeHandler({
    'GET /auth/me/': () => [200, { ...APPLICANT, phone: '05551112233' }],
    'GET /services/': () => [200, SERVICES],
    ...extra,
  }))
}

/**
 * Etiketiyle bulunan alana değer yazar.
 *
 * @param {string} label Etiketin başlangıcı.
 * @param {string} value Değer.
 */
async function fill(label, value) {
  const labelEl = wrapper.findAll('label').find((item) => item.text().startsWith(label))
  await wrapper.get(`#${labelEl.attributes('for')}`).setValue(value)
}

/** Formu gönderir (Devam et / Başvuruyu gönder). */
async function proceed() {
  await wrapper.get('form').trigger('submit')
  await flushPromises()
}

const title = () => wrapper.get('h1').text()

beforeEach(() => window.sessionStorage.clear())
afterEach(() => wrapper?.unmount())

describe('yeni başvuru sayfası', () => {
  it('beş adımı doldurup başvuruyu gönderir ve detaya gider', async () => {
    signedIn({ 'POST /requests/': () => [201, { id: 21 }] })
    const mounted = await mountApp('/requests/new')
    wrapper = mounted.wrapper

    expect(title()).toBe('Hangi konuda desteğe ihtiyacınız var?')
    await wrapper.findAll('input[type="radio"]')[1].setValue(true)
    await proceed()

    expect(title()).toBe('Destek kimin için?')
    await fill('Adı ve soyadı', 'Fatma Yılmaz')
    await fill('Yaşı', '78')
    await wrapper.get('select').setValue('parent')
    await proceed()

    expect(title()).toBe('Ne zaman ve nerede?')
    await fill('Hangi gün', isoDateAfter(3))
    await wrapper.get('select').setValue('afternoon')
    await fill('İl', 'Samsun')
    await fill('İlçe', 'İlkadım')
    await fill('Açık adres', 'Örnek Mah. No: 1')
    await proceed()

    expect(title()).toBe('Size nasıl ulaşalım?')
    await proceed()

    expect(title()).toBe('Son bir kontrol')
    expect(wrapper.text()).toContain('Hastane eşliği')
    expect(wrapper.text()).toContain('Öğleden sonra (12:00-17:00)')
    await wrapper.get('input[type="checkbox"]').setValue(true)
    await proceed()

    const payload = JSON.parse(calls.find((call) => call.url === '/requests/').data)
    expect(payload).toMatchObject({
      service: 4, elder_full_name: 'Fatma Yılmaz', elder_age: 78, relationship: 'parent',
      time_slot: 'afternoon', contact_phone: '05551112233', consent: true,
    })
    await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/requests/21?created=1'), { timeout: 5000 })
  })

  it('eksik bilgiyle ilerlemez ve hatayı gösterir', async () => {
    signedIn()
    ;({ wrapper } = await mountApp('/requests/new'))

    await proceed()

    expect(title()).toBe('Hangi konuda desteğe ihtiyacınız var?')
    expect(wrapper.text()).toContain('Devam etmek için bir hizmet seçin.')
  })

  it('ana sayfadaki hizmet bağlantısından gelince hizmet seçili başlar', async () => {
    signedIn()
    ;({ wrapper } = await mountApp('/requests/new?service=3'))

    expect(wrapper.findAll('input[type="radio"]')[0].element.checked).toBe(true)
  })

  it('özetteki Düzenle düğmesi ilgili adıma döner ve geri düğmesi bir adım geri gider', async () => {
    signedIn()
    window.sessionStorage.setItem('yanimda.requestDraft', JSON.stringify({
      step: 4,
      form: {
        service: 3, elder_full_name: 'Fatma Yılmaz', elder_age: '78', relationship: 'parent',
        preferred_date: isoDateAfter(3), time_slot: 'morning', city: 'Samsun', district: 'İlkadım',
        address: 'No: 1', contact_phone: '05551112233',
      },
    }))
    ;({ wrapper } = await mountApp('/requests/new'))
    expect(title()).toBe('Son bir kontrol')

    const editButtons = wrapper.findAll('.summary-section button')
    await editButtons[1].trigger('click')
    expect(title()).toBe('Destek kimin için?')

    const back = wrapper.findAll('button').find((button) => button.text() === 'Geri dön')
    await back.trigger('click')
    expect(title()).toBe('Hangi konuda desteğe ihtiyacınız var?')
  })

  it('sunucu mükerrer başvuruyu reddederse hizmet adımında mesajı gösterir', async () => {
    signedIn({ 'POST /requests/': () => [400, { service: ['Fatma Yılmaz için bu hizmette zaten açık bir başvurunuz var.'] }] })
    window.sessionStorage.setItem('yanimda.requestDraft', JSON.stringify({
      step: 4,
      form: {
        service: 3, elder_full_name: 'Fatma Yılmaz', elder_age: '78', relationship: 'parent',
        preferred_date: isoDateAfter(3), time_slot: 'morning', city: 'Samsun', district: 'İlkadım',
        address: 'No: 1', contact_phone: '05551112233', consent: true,
      },
    }))
    ;({ wrapper } = await mountApp('/requests/new'))

    await proceed()

    expect(title()).toBe('Hangi konuda desteğe ihtiyacınız var?')
    expect(wrapper.text()).toContain('zaten açık bir başvurunuz var')
  })
})
