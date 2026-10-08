import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { axeViolations } from '../helpers/axe'
import { ADMIN, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { inquiryRow, mapResponse, requestRow, stubBoundaryFetch, stubMatchMedia } from '../helpers/map'
import { mountApp } from '../helpers/mountApp'
import { page } from '../helpers/requests'

// MapLibre jsdom'da çizemez; harita yerine boş bir kutu bırakılır (sıralama listesi ayrıca denetlenir).
vi.mock('@/components/admin/map/ThematicMap.vue', async () => {
  const { h } = await import('vue')
  return {
    default: {
      name: 'ThematicMap',
      props: ['boundaries', 'districts', 'neighborhoods', 'total', 'serviceId', 'theme'],
      emits: ['select', 'level'],
      setup: () => () => h('div', { class: 'map-stub' }),
    },
  }
})

let wrapper
let restoreMatchMedia

beforeEach(() => {
  stubBoundaryFetch()
  restoreMatchMedia = stubMatchMedia()
})

afterEach(() => {
  wrapper?.unmount()
  document.body.innerHTML = ''
  vi.unstubAllGlobals()
  restoreMatchMedia()
  restoreApi()
  window.localStorage.clear()
})

/** Admin oturumuyla veriyle dolu harita sayfasını açar. */
async function openMap() {
  tokenStorage.set({ access: 'a1', refresh: 'r1' })
  useFakeApi(routeHandler({
    'GET /auth/me/': () => [200, ADMIN],
    'GET /admin/map/': () => [200, mapResponse()],
    'GET /admin/requests/': () => [200, page([requestRow(1), requestRow(2)])],
    'GET /admin/inquiries/': () => [200, page([inquiryRow(7)])],
  }))
  ;({ wrapper } = await mountApp('/admin/map'))
  await vi.waitFor(() => expect(wrapper.find('.ranking__row').exists()).toBe(true), { timeout: 5000 })
  await flushPromises()
}

describe('talep haritası erişilebilirliği', () => {
  it('harita, lejant ve sıralama listesi axe ihlali içermez', async () => {
    await openMap()

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('açık kayıt çekmecesi axe ihlali içermez', async () => {
    await openMap()
    await wrapper.get('[data-area="district-5"]').trigger('click')
    await vi.waitFor(() => expect(document.body.querySelector('.area-drawer .area-drawer__item')).not.toBeNull(), { timeout: 5000 })
    await flushPromises()

    expect(await axeViolations(document.body.querySelector('.area-drawer'))).toEqual([])
  })
})
