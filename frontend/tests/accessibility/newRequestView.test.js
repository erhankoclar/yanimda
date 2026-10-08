import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'
import { isoDateAfter } from '@/utils/dates'

import { axeViolations } from '../helpers/axe'
import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

const FORM = {
  service: 3, elder_full_name: 'Fatma Yılmaz', elder_age: '78', relationship: 'parent',
  preferred_date: isoDateAfter(3), time_slot: 'morning', district: 5, neighborhood: 11,
  address: 'No: 1', contact_phone: '05551112233',
}

let wrapper

// Sihirbaz ve ayrıştırıcı parçaları tembel yüklenir; ilk testin soğuk derlemeye takılmaması için önceden ısıtılır.
beforeAll(async () => {
  await Promise.all([
    import('@/layouts/PublicLayout.vue'),
    import('@/views/public/NewRequestView.vue'),
  ])
}, 120000)

// axe-core aynı anda tek çalıştırmayı destekler; bir test başarısız olsa bile sonraki testin
// çakışmaması için her testten sonra çalışan taramanın bitmesi beklenir.
let axeQueue = Promise.resolve()

/**
 * axe taramasını sıraya koyar; önceki tarama (hata verse de) bitmeden yenisi başlamaz.
 *
 * @param {Element} element Denetlenecek kök öğe.
 * @returns {Promise<Array>} İhlaller.
 */
function scan(element) {
  const run = axeQueue.catch(() => {}).then(() => axeViolations(element))
  axeQueue = run
  return run
}

afterEach(async () => {
  await axeQueue.catch(() => {})
  wrapper?.unmount()
  window.sessionStorage.clear()
})

describe('başvuru sihirbazı erişilebilirliği', () => {
  it.each([0, 1, 2, 3, 4])('%i. adım boş ve hatalı haliyle axe ihlali içermez', async (step) => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, APPLICANT],
      'GET /services/': () => [200, [{ id: 3, name: 'Refakat', slug: 'r', description: 'd', icon: 'companion' }]],
    }))
    window.sessionStorage.setItem('yanimda.requestDraft', JSON.stringify({ step, form: step === 4 ? FORM : {} }))
    ;({ wrapper } = await mountApp('/requests/new'))
    expect(await scan(wrapper.element)).toEqual([])

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(await scan(wrapper.element)).toEqual([])
  })

  it('konum adımı ilçe ve mahalle seçiliyken ve mahalle kapalıyken axe ihlali içermez', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, APPLICANT],
      'GET /services/': () => [200, [{ id: 3, name: 'Refakat', slug: 'r', description: 'd', icon: 'companion' }]],
    }))
    window.sessionStorage.setItem('yanimda.requestDraft', JSON.stringify({ step: 2, form: {} }))
    ;({ wrapper } = await mountApp('/requests/new'))
    expect(wrapper.findAll('select')[2].attributes('disabled')).toBeDefined()
    expect(await scan(wrapper.element)).toEqual([])

    await wrapper.findAll('select')[1].setValue(5)
    await flushPromises()
    await wrapper.findAll('select')[2].setValue(11)

    expect(wrapper.findAll('select')[2].attributes('disabled')).toBeUndefined()
    expect(await scan(wrapper.element)).toEqual([])
  })

  it('adım geçişinde odak yeni adımın başlığına taşınır', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [200, APPLICANT],
      'GET /services/': () => [200, [{ id: 3, name: 'Refakat', slug: 'r', description: 'd', icon: 'companion' }]],
    }))
    ;({ wrapper } = await mountApp('/requests/new?service=3'))

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(document.activeElement).toBe(wrapper.get('h1').element)
    expect(document.activeElement.textContent).toBe('Destek kimin için?')
  })
})
