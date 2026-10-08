import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'
import { isoDateAfter } from '@/utils/dates'

import { ADMIN, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { inquiryRow, mapResponse, requestRow, stubBoundaryFetch, stubMatchMedia } from '../helpers/map'
import { mountApp } from '../helpers/mountApp'
import { page } from '../helpers/requests'

// MapLibre jsdom'da WebGL çizemez; harita bileşeni aldığı özellikleri kaydeden ve olay yollayabilen bir taklitle değiştirilir.
const mapStub = vi.hoisted(() => ({ props: null, emit: null }))
vi.mock('@/components/admin/map/ThematicMap.vue', async () => {
  const { h } = await import('vue')
  return {
    default: {
      name: 'ThematicMap',
      props: ['boundaries', 'districts', 'neighborhoods', 'total', 'serviceId', 'theme'],
      emits: ['select', 'level'],
      setup(props, { emit }) {
        mapStub.emit = emit
        return () => {
          mapStub.props = props
          return h('div', { class: 'map-stub', 'data-total': props.total, 'data-service': props.serviceId ?? '' })
        }
      },
    },
  }
})

let wrapper
let restoreMatchMedia

beforeEach(() => {
  stubBoundaryFetch()
  restoreMatchMedia = stubMatchMedia()
  mapStub.props = null
})

afterEach(() => {
  wrapper?.unmount()
  document.body.innerHTML = ''
  vi.unstubAllGlobals()
  restoreMatchMedia()
  restoreApi()
  window.localStorage.clear()
})

/**
 * Admin oturumu ve verilen yanıtlayıcılarla harita sayfasını açar.
 *
 * @param {Record<string, (config: object) => [number, any]>} [routes] Ek ya da ezilen uç nokta yanıtlayıcıları.
 * @param {{ waitForMap?: boolean }} [options] false ise harita taklidinin görünmesi beklenmez (hata senaryosu).
 * @returns {Promise<Array<object>>} İstek kaydı.
 */
async function openMap(routes = {}, { waitForMap = true } = {}) {
  tokenStorage.set({ access: 'a1', refresh: 'r1' })
  const calls = useFakeApi(routeHandler({
    'GET /auth/me/': () => [200, ADMIN],
    'GET /admin/map/': () => [200, mapResponse()],
    'GET /admin/requests/': () => [200, page([requestRow(1), requestRow(2)])],
    'GET /admin/inquiries/': () => [200, page([inquiryRow(7)])],
    ...routes,
  }))
  ;({ wrapper } = await mountApp('/admin/map'))
  if (waitForMap) await vi.waitFor(() => expect(wrapper.find('.map-stub').exists()).toBe(true), { timeout: 5000 })
  await flushPromises()
  return calls
}

const callsTo = (calls, url) => calls.filter((call) => call.url === url)
const total = () => wrapper.get('.map-page__total strong').text()
const rankingNames = () => wrapper.findAll('.ranking__name').map((node) => node.text())

/**
 * Verilen etiketli seçim grubunda metinli düğmeye basar.
 *
 * @param {string} group Grubun aria-label değeri.
 * @param {string} label Düğme metni.
 */
async function choose(group, label) {
  const button = wrapper.get(`[aria-label="${group}"]`).findAll('button').find((item) => item.text() === label)
  await button.trigger('click')
  await flushPromises()
}

/**
 * Hizmet açılır listesinin değerini değiştirir.
 *
 * @param {number} id Hizmet kimliği; 0 tüm hizmetler.
 */
async function chooseService(id) {
  wrapper.findComponent({ name: 'Select' }).vm.$emit('update:modelValue', id)
  await flushPromises()
}

describe('talep haritası sayfası', () => {
  it('varsayılan olarak tüm kaynaklar ve tüm dönemle yükler; üç sınır dosyasını indirir', async () => {
    const fetchMock = stubBoundaryFetch()
    const calls = await openMap()

    expect(callsTo(calls, '/admin/map/')[0].params).toEqual({ source: 'all' })
    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(fetchMock.mock.calls.map(([url]) => url).sort()).toEqual([
      expect.stringContaining('istanbul-districts.geojson'),
      expect.stringContaining('istanbul-labels.geojson'),
      expect.stringContaining('istanbul-neighborhoods.geojson'),
    ])
  })

  it('araç çubuğunda il toplamını gösterir ve haritaya sınır ile sayıları verir', async () => {
    await openMap()

    expect(total()).toBe('9')
    expect(wrapper.get('.map-page__total-label').text()).toBe('İstanbul geneli')
    expect(mapStub.props.total).toBe(9)
    expect(mapStub.props.districts).toHaveLength(3)
    expect(mapStub.props.neighborhoods).toHaveLength(3)
    expect(Object.keys(mapStub.props.boundaries)).toEqual(['districts', 'neighborhoods', 'labels'])
  })

  it('sıralamayı kaydı olan ilçelerle çoktan aza listeler; talep gelmeyen ilçeyi ayrıca yazar', async () => {
    await openMap()

    expect(rankingNames()).toEqual(['Kadıköy', 'Üsküdar'])
    expect(wrapper.get('.ranking__none').text()).toBe('Talep gelmeyen 1 ilçe: Adalar')
  })

  it('hizmet seçimi toplamı ve sıralamayı yeni istek yapmadan değiştirir', async () => {
    const calls = await openMap()

    await chooseService(2)

    expect(total()).toBe('3')
    expect(wrapper.get('.map-page__total-label').text()).toBe('Alışveriş desteği')
    expect(mapStub.props.serviceId).toBe(2)
    expect(mapStub.props.total).toBe(3)
    expect(wrapper.findAll('.ranking__count').map((node) => node.text())).toEqual(['2', '1'])
    expect(callsTo(calls, '/admin/map/')).toHaveLength(1)

    await chooseService(1)

    expect(total()).toBe('6')
    expect(wrapper.findAll('.ranking__count').map((node) => node.text())).toEqual(['5', '1'])
    expect(callsTo(calls, '/admin/map/')).toHaveLength(1)
  })

  it('hizmet listesi her hizmeti kayıt sayısıyla sunar', async () => {
    await openMap()

    const options = wrapper.findComponent({ name: 'Select' }).props('options')
    expect(options.map((option) => option.label)).toEqual(['Tüm hizmetler', 'Evde bakım (6)', 'Alışveriş desteği (3)'])
  })

  it('kaynak seçimi haritayı yeni parametreyle yeniden ister', async () => {
    const calls = await openMap()

    await choose('Kaynak', 'Başvurular')

    expect(callsTo(calls, '/admin/map/').map((call) => call.params)).toEqual([{ source: 'all' }, { source: 'requests' }])
  })

  it('dönem seçimi days parametresini ekler; Tümü seçilince kaldırır', async () => {
    const calls = await openMap()

    await choose('Dönem', 'Son 90 gün')
    await choose('Dönem', 'Tümü')

    expect(callsTo(calls, '/admin/map/').map((call) => call.params)).toEqual([
      { source: 'all' }, { source: 'all', days: 90 }, { source: 'all' },
    ])
  })

  it('kaynak ve dönem birlikte seçilince ikisini de yollar', async () => {
    const calls = await openMap()

    await choose('Dönem', 'Son 30 gün')
    await choose('Kaynak', 'Hızlı talepler')

    expect(callsTo(calls, '/admin/map/').at(-1).params).toEqual({ source: 'inquiries', days: 30 })
  })

  it('yüklenemezse hata gösterir; tekrar dene ile yeniden ister', async () => {
    let fail = true
    const calls = await openMap({ 'GET /admin/map/': () => (fail ? [500, {}] : [200, mapResponse()]) }, { waitForMap: false })

    expect(wrapper.get('[role="alert"]').text()).toContain('Tekrar dene')
    expect(wrapper.find('.map-stub').exists()).toBe(false)
    fail = false
    await wrapper.get('[role="alert"] button').trigger('click')
    await vi.waitFor(() => expect(wrapper.find('.map-stub').exists()).toBe(true))
    await flushPromises()

    expect(callsTo(calls, '/admin/map/')).toHaveLength(2)
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(total()).toBe('9')
  })

  it('haritadaki seviye mahalleye geçince sıralama mahalleleri listeler', async () => {
    await openMap()

    mapStub.emit('level', 'neighborhood')
    await flushPromises()

    expect(rankingNames()).toEqual(['Moda Mahallesi', 'Caferağa Mahallesi', 'Altunizade Mahallesi'])
  })

  it('dil değişince haritayı yeniden ister', async () => {
    const calls = await openMap()

    await wrapper.findAll('.preference-controls__flag')[1].trigger('click')
    await flushPromises()

    expect(callsTo(calls, '/admin/map/')).toHaveLength(2)
  })
})

describe('alan kayıtları çekmecesi', () => {
  const drawer = () => document.body.querySelector('.area-drawer')
  const drawerButtons = () => [...drawer().querySelectorAll('button')]

  /**
   * Çekmecedeki metinli düğmeye basar.
   *
   * @param {string} label Düğme metni.
   */
  async function pressInDrawer(label) {
    drawerButtons().find((button) => button.textContent.trim() === label).click()
    await flushPromises()
  }

  /** Sıralamadaki Kadıköy satırına tıklar ve çekmece yüklenene kadar bekler. */
  async function openKadikoy() {
    await wrapper.get('[data-area="district-5"]').trigger('click')
    await vi.waitFor(() => expect(drawer()).not.toBeNull())
    await flushPromises()
  }

  it('sıralama satırına tıklanınca çekmeceyi açar ve başvuruları ilçe süzgeciyle ister', async () => {
    const calls = await openMap()

    await openKadikoy()

    expect(callsTo(calls, '/admin/requests/')).toHaveLength(1)
    expect(callsTo(calls, '/admin/requests/')[0].params).toEqual({ page: 1, district: 5 })
    expect(drawer().querySelector('h2').textContent).toBe('Kadıköy')
    expect(drawer().textContent).toContain('Haritada 7 kayıt')
    expect(drawer().querySelectorAll('.area-drawer__item')).toHaveLength(2)
  })

  it('hizmet ve dönem seçiliyse service ve created_from süzgeçlerini ekler', async () => {
    const calls = await openMap()
    await choose('Dönem', 'Son 30 gün')
    await chooseService(1)

    await openKadikoy()

    expect(callsTo(calls, '/admin/requests/')[0].params).toEqual({
      page: 1, district: 5, service: 1, created_from: isoDateAfter(-29),
    })
  })

  it('mahalle satırı neighborhood süzgeciyle ister', async () => {
    const calls = await openMap()
    mapStub.emit('level', 'neighborhood')
    await flushPromises()

    await wrapper.get('[data-area="neighborhood-12"]').trigger('click')
    await vi.waitFor(() => expect(drawer()).not.toBeNull())
    await flushPromises()

    expect(callsTo(calls, '/admin/requests/')[0].params).toEqual({ page: 1, neighborhood: 12 })
  })

  it('haritadan gelen select olayı da çekmeceyi açar', async () => {
    const calls = await openMap()

    mapStub.emit('select', { level: 'district', id: 6, name: 'Üsküdar', count: 2 })
    await vi.waitFor(() => expect(drawer()).not.toBeNull())
    await flushPromises()

    expect(callsTo(calls, '/admin/requests/')[0].params).toEqual({ page: 1, district: 6 })
  })

  it('türü Hızlı talepler yapınca aynı süzgeçlerle hızlı talepleri ister', async () => {
    const calls = await openMap()
    await chooseService(2)
    await openKadikoy()

    await pressInDrawer('Hızlı talepler')

    expect(callsTo(calls, '/admin/inquiries/')).toHaveLength(1)
    expect(callsTo(calls, '/admin/inquiries/')[0].params).toEqual({ page: 1, district: 5, service: 2 })
    expect(drawer().textContent).toContain('Kişi 7')
  })

  it('kaynak tek türe süzülmüşse tür seçicisini göstermez ve o türü ister', async () => {
    const calls = await openMap()
    await choose('Kaynak', 'Hızlı talepler')

    await openKadikoy()

    expect(callsTo(calls, '/admin/requests/')).toHaveLength(0)
    expect(callsTo(calls, '/admin/inquiries/')[0].params).toEqual({ page: 1, district: 5 })
    expect(drawer().querySelector('[aria-label="Kayıt türü"]')).toBeNull()
  })

  it('sonraki sayfa varsa Daha fazla göster ikinci sayfayı ister ve listeye ekler', async () => {
    const calls = await openMap({
      'GET /admin/requests/': (config) => (config.params.page === 2
        ? [200, page([requestRow(3)])]
        : [200, page([requestRow(1), requestRow(2)], 'http://x/?page=2')]),
    })
    await openKadikoy()

    await pressInDrawer('Daha fazla göster')

    expect(callsTo(calls, '/admin/requests/').map((call) => call.params.page)).toEqual([1, 2])
    expect(drawer().querySelectorAll('.area-drawer__item')).toHaveLength(3)
    expect(drawerButtons().some((button) => button.textContent.trim() === 'Daha fazla göster')).toBe(false)
  })

  it('kayıt yoksa boş durum metnini gösterir', async () => {
    await openMap({ 'GET /admin/requests/': () => [200, page([])] })

    await openKadikoy()

    expect(drawer().textContent).toContain('Bu alanda seçime uyan kayıt yok.')
  })

  it('liste yüklenemezse çekmecede hata gösterir', async () => {
    await openMap({ 'GET /admin/requests/': () => [500, {}] })

    await openKadikoy()

    expect(drawer().querySelector('[role="alert"]')).not.toBeNull()
  })
})
