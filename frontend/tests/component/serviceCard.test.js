import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { h, ref } from 'vue'

import ServiceCard from '@/components/public/ServiceCard.vue'
import WizardProgress from '@/components/public/WizardProgress.vue'

const SERVICES = [
  { id: 1, name: 'Refakat ve sohbet', description: 'Düzenli ziyaret', icon: 'companion' },
  { id: 2, name: 'Hastane eşliği', description: 'Randevulara eşlik', icon: 'hospital' },
]

/**
 * İki hizmet kartını ortak seçimle bağlar.
 *
 * @param {number | null} initial Başlangıçta seçili hizmet kimliği.
 * @returns {{ wrapper: import('@vue/test-utils').VueWrapper, selected: import('vue').Ref<number | null> }} Kart grubu ve seçim.
 */
function mountGroup(initial = null) {
  const selected = ref(initial)
  const wrapper = mount({
    setup: () => () => h('div', { role: 'radiogroup' }, SERVICES.map((service) => h(ServiceCard, {
      service,
      name: 'service',
      modelValue: selected.value,
      'onUpdate:modelValue': (value) => { selected.value = value },
    }))),
  }, { attachTo: document.body })
  return { wrapper, selected }
}

describe('ServiceCard', () => {
  it('hizmet adı ve açıklamasını gösterir', () => {
    const { wrapper } = mountGroup()

    expect(wrapper.text()).toContain('Refakat ve sohbet')
    expect(wrapper.text()).toContain('Randevulara eşlik')
    wrapper.unmount()
  })

  it('karta tıklanınca hizmeti seçer ve yalnızca o kart seçili görünür', async () => {
    const { wrapper, selected } = mountGroup()

    await wrapper.findAll('input')[1].setValue(true)

    expect(selected.value).toBe(2)
    const cards = wrapper.findAll('.service-card')
    expect(cards[1].classes()).toContain('service-card--selected')
    expect(cards[0].classes()).not.toContain('service-card--selected')
    wrapper.unmount()
  })

  it('kartlar aynı radyo grubunda, klavyeyle erişilebilir yerel radyo düğmeleridir', () => {
    const { wrapper } = mountGroup(1)

    const radios = wrapper.findAll('input[type="radio"]')
    expect(radios).toHaveLength(2)
    expect(new Set(radios.map((radio) => radio.attributes('name')))).toEqual(new Set(['service']))
    expect(radios[0].element.checked).toBe(true)
    wrapper.unmount()
  })
})

describe('WizardProgress', () => {
  it('etkin adımı özetler ve aria-current ile işaretler', () => {
    const wrapper = mount(WizardProgress, { props: { steps: ['Hizmet', 'Yakınınız', 'Özet'], current: 1 } })

    expect(wrapper.text()).toContain('Adım 2 / 3')
    expect(wrapper.get('[aria-current="step"]').text()).toBe('Yakınınız')
    expect(wrapper.findAll('li')[0].text()).toContain('tamamlandı')
  })
})
