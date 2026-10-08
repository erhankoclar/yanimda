import { mount } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import { describe, expect, it } from 'vitest'

import AreaRanking from '@/components/admin/map/AreaRanking.vue'
import MapLegend from '@/components/admin/map/MapLegend.vue'

describe('MapLegend', () => {
  it('her sınıf için renk kutusu ve aralık metni gösterir', () => {
    const wrapper = mount(MapLegend, { props: { values: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] } })

    const rows = wrapper.findAll('li')
    expect(rows.map((row) => row.text())).toEqual(['1–2', '3–4', '5–6', '7–8', '9–10'])
    expect(wrapper.findAll('.map-legend__swatch')).toHaveLength(5)
    expect(wrapper.get('.map-legend__swatch').attributes('aria-hidden')).toBe('true')
  })

  it('tek değerli sınıfı aralıksız yazar', () => {
    const wrapper = mount(MapLegend, { props: { values: [4] } })

    expect(wrapper.findAll('li').map((row) => row.text())).toEqual(['4'])
  })

  it('binlik sayıları Türkçe biçimlendirir', () => {
    const wrapper = mount(MapLegend, { props: { values: [1200] } })

    expect(wrapper.get('li').text()).toBe('1.200')
  })

  it('kayıt yoksa boş durum metnini gösterir ve liste çizmez', () => {
    const wrapper = mount(MapLegend, { props: { values: [0, 0] } })

    expect(wrapper.get('.map-legend__empty').text()).toBe('Bu seçimde kayıt yok')
    expect(wrapper.find('ul').exists()).toBe(false)
    expect(wrapper.get('.map-legend__title').text()).toBe('Talep sayısı')
  })

  it('temaya göre farklı renkler kullanır', () => {
    const light = mount(MapLegend, { props: { values: [3], theme: 'light' } })
    const dark = mount(MapLegend, { props: { values: [3], theme: 'dark' } })

    expect(light.get('.map-legend__swatch').attributes('style')).not.toBe(dark.get('.map-legend__swatch').attributes('style'))
  })
})

const DISTRICTS = [
  { id: 1, osm_id: 1001, name: 'Kadıköy', count: 8, by_service: { 1: 6, 2: 2 } },
  { id: 2, osm_id: 1002, name: 'Şile', count: 4, by_service: { 1: 4 } },
  { id: 3, osm_id: 1003, name: 'Sarıyer', count: 4, by_service: { 2: 4 } },
  { id: 4, osm_id: 1004, name: 'Adalar', count: 0, by_service: {} },
  { id: 5, osm_id: 1005, name: 'Beykoz', count: 0, by_service: {} },
]
const NEIGHBORHOODS = [
  { id: 11, osm_id: 2011, name: 'Moda Mahallesi', district_id: 1, count: 5, by_service: { 1: 5 } },
  { id: 12, osm_id: 2012, name: 'Caferağa Mahallesi', district_id: 1, count: 3, by_service: { 1: 1, 2: 2 } },
]

/**
 * Sıralama panelini v-model:level bağıyla bağlar.
 *
 * @param {Record<string, any>} [props] Ek prop değerleri.
 * @returns {import('@vue/test-utils').VueWrapper} Bağlanmış panel.
 */
function mountRanking(props = {}) {
  const wrapper = mount(AreaRanking, {
    props: {
      districts: DISTRICTS,
      neighborhoods: NEIGHBORHOODS,
      level: 'district',
      'onUpdate:level': (value) => wrapper.setProps({ level: value }),
      ...props,
    },
    global: { plugins: [PrimeVue] },
  })
  return wrapper
}

const names = (wrapper) => wrapper.findAll('.ranking__name').map((node) => node.text())

describe('AreaRanking', () => {
  it('yalnızca kaydı olan ilçeleri çoktan aza, eşitlikte Türkçe ad sırasıyla listeler', () => {
    const wrapper = mountRanking()

    expect(names(wrapper)).toEqual(['Kadıköy', 'Sarıyer', 'Şile'])
    expect(wrapper.findAll('.ranking__rank').map((node) => node.text())).toEqual(['1', '2', '3'])
    expect(wrapper.findAll('.ranking__count').map((node) => node.text())).toEqual(['8', '4', '4'])
  })

  it('çubuk genişliklerini en yüksek değere oranlar', () => {
    const wrapper = mountRanking()

    const widths = wrapper.findAll('.ranking__bar span').map((node) => node.attributes('style'))
    expect(widths).toEqual(['width: 100%;', 'width: 50%;', 'width: 50%;'])
  })

  it('düzey değiştirilince mahalleleri listeler', async () => {
    const wrapper = mountRanking()

    const button = wrapper.findAll('button').find((node) => node.text() === 'Mahalleler')
    await button.trigger('click')

    expect(wrapper.emitted('update:level')[0]).toEqual(['neighborhood'])
    expect(names(wrapper)).toEqual(['Moda Mahallesi', 'Caferağa Mahallesi'])
  })

  it('düzey prop olarak verilince mahalle listesiyle açılır', () => {
    const wrapper = mountRanking({ level: 'neighborhood' })

    expect(names(wrapper)).toEqual(['Moda Mahallesi', 'Caferağa Mahallesi'])
  })

  it('satıra tıklanınca düzey, kimlik, ad ve sayıyı select olayıyla yollar', async () => {
    const wrapper = mountRanking()

    await wrapper.get('[data-area="district-3"]').trigger('click')

    expect(wrapper.emitted('select')[0]).toEqual([{ level: 'district', id: 3, name: 'Sarıyer', count: 4 }])
  })

  it('mahalle satırında düzeyi neighborhood olarak yollar', async () => {
    const wrapper = mountRanking({ level: 'neighborhood' })

    await wrapper.get('[data-area="neighborhood-11"]').trigger('click')

    expect(wrapper.emitted('select')[0]).toEqual([{ level: 'neighborhood', id: 11, name: 'Moda Mahallesi', count: 5 }])
  })

  it('hizmet seçiliyse sayıları ve sıralamayı o hizmete göre yapar', () => {
    const wrapper = mountRanking({ serviceId: 2 })

    expect(names(wrapper)).toEqual(['Sarıyer', 'Kadıköy'])
    expect(wrapper.findAll('.ranking__count').map((node) => node.text())).toEqual(['4', '2'])
    expect(wrapper.findAll('.ranking__bar span').map((node) => node.attributes('style'))).toEqual(['width: 100%;', 'width: 50%;'])
  })

  it('talep gelmeyen ilçeleri ilçe düzeyinde sayı ve adlarıyla yazar', () => {
    const wrapper = mountRanking()

    expect(wrapper.get('.ranking__none').text()).toBe('Talep gelmeyen 2 ilçe: Adalar, Beykoz')
  })

  it('mahalle düzeyinde talep gelmeyen ilçeler satırını göstermez', () => {
    const wrapper = mountRanking({ level: 'neighborhood' })

    expect(wrapper.find('.ranking__none').exists()).toBe(false)
  })

  it('hiç ilçe boş değilse talep gelmeyen satırını göstermez', () => {
    const wrapper = mountRanking({ districts: DISTRICTS.slice(0, 3) })

    expect(wrapper.find('.ranking__none').exists()).toBe(false)
  })

  it('kayıt yoksa boş durum metnini gösterir', () => {
    const wrapper = mountRanking({ districts: [], neighborhoods: [] })

    expect(wrapper.get('.ranking__empty').text()).toBe('Bu seçimde kayıt yok.')
    expect(wrapper.find('ol').exists()).toBe(false)
  })
})
