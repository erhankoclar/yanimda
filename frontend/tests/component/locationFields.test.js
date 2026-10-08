import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import LocationFields from '@/components/public/LocationFields.vue'

import { routeHandler, useFakeApi } from '../helpers/fakeApi'

/**
 * Bileşeni v-model bağlarıyla bağlar; seçimleri `selection` nesnesinde tutar.
 *
 * @param {Record<string, any>} [props] Ek prop değerleri (ör. errors, başlangıç seçimleri).
 * @returns {Promise<import('@vue/test-utils').VueWrapper>} Bağlanmış bileşen.
 */
async function mountFields(props = {}) {
  const wrapper = mount(LocationFields, {
    props: {
      district: '',
      neighborhood: '',
      'onUpdate:district': (value) => wrapper.setProps({ district: value }),
      'onUpdate:neighborhood': (value) => wrapper.setProps({ neighborhood: value }),
      ...props,
    },
  })
  await flushPromises()
  return wrapper
}

const selects = (wrapper) => wrapper.findAll('select')
const optionTexts = (select) => select.findAll('option').map((option) => option.text())

describe('LocationFields', () => {
  it('ilçeleri listeler ve ilçe seçilene kadar mahalle alanını kapalı tutar', async () => {
    const wrapper = await mountFields()

    const [district, neighborhood] = selects(wrapper)
    expect(optionTexts(district)).toEqual(['Seçin', 'Kadıköy', 'Üsküdar'])
    expect(neighborhood.attributes('disabled')).toBeDefined()
    expect(optionTexts(neighborhood)).toEqual(['Önce ilçe seçin'])
  })

  it('ilçe seçilince mahalleleri yükler ve mahalle alanını açar', async () => {
    const wrapper = await mountFields()

    await selects(wrapper)[0].setValue(5)
    await flushPromises()

    const neighborhood = selects(wrapper)[1]
    expect(neighborhood.attributes('disabled')).toBeUndefined()
    expect(optionTexts(neighborhood)).toEqual(['Seçin', 'Caferağa Mahallesi', 'Moda Mahallesi'])
  })

  it('ilçe değişince seçili mahalleyi temizler', async () => {
    const wrapper = await mountFields()
    await selects(wrapper)[0].setValue(5)
    await flushPromises()
    await selects(wrapper)[1].setValue(12)
    expect(wrapper.props('neighborhood')).toBe(12)

    await selects(wrapper)[0].setValue(6)
    await flushPromises()

    expect(wrapper.props('district')).toBe(6)
    expect(wrapper.props('neighborhood')).toBe('')
    expect(optionTexts(selects(wrapper)[1])).toEqual(['Seçin', 'Altunizade Mahallesi'])
  })

  it('başlangıçta ilçe verilmişse mahallelerini hemen yükler ve seçili mahalleyi korur', async () => {
    const wrapper = await mountFields({ district: 5, neighborhood: 11 })

    expect(selects(wrapper)[1].element.value).toBe('11')
    expect(wrapper.props('neighborhood')).toBe(11)
  })

  it('hata mesajlarını ilgili alanın altında gösterir', async () => {
    const wrapper = await mountFields({ errors: { district: 'İlçe seçin.', neighborhood: 'Mahalle seçin.' } })

    const [district, neighborhood] = selects(wrapper)
    expect(district.attributes('aria-invalid')).toBe('true')
    expect(neighborhood.attributes('aria-invalid')).toBe('true')
    expect(wrapper.text()).toContain('İlçe seçin.')
    expect(wrapper.text()).toContain('Mahalle seçin.')
  })

  it('listeleri önbelleğe alır; ikinci bağlamada aynı istekleri tekrarlamaz', async () => {
    const calls = useFakeApi(routeHandler({}))
    const first = await mountFields()
    await selects(first)[0].setValue(5)
    await flushPromises()
    first.unmount()

    const second = await mountFields({ district: 5 })

    const urls = calls.map((call) => call.url)
    expect(urls.filter((url) => url === '/geo/districts/')).toHaveLength(1)
    expect(urls.filter((url) => url === '/geo/districts/5/neighborhoods/')).toHaveLength(1)
    expect(optionTexts(selects(second)[0])).toContain('Kadıköy')
    expect(optionTexts(selects(second)[1])).toContain('Moda Mahallesi')
  })

  it('ilçe listesi yüklenemezse çökmez ve sonraki bağlamada yeniden dener', async () => {
    let attempts = 0
    const calls = useFakeApi(routeHandler({
      'GET /geo/districts/': () => { attempts += 1; return attempts === 1 ? [500, {}] : [200, [{ id: 5, name: 'Kadıköy' }]] },
    }))
    const failed = await mountFields()
    expect(optionTexts(selects(failed)[0])).toEqual(['Seçin'])
    failed.unmount()

    const retried = await mountFields()

    expect(calls.filter((call) => call.url === '/geo/districts/')).toHaveLength(2)
    expect(optionTexts(selects(retried)[0])).toEqual(['Seçin', 'Kadıköy'])
  })
})
