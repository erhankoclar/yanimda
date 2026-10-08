import { mount } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import { describe, expect, it } from 'vitest'

import StatCard from '@/components/admin/StatCard.vue'

/**
 * Kartı PrimeVue ile bağlar.
 *
 * @param {object} props Kart özellikleri.
 * @returns {import('@vue/test-utils').VueWrapper} Bağlanmış kart.
 */
function mountCard(props) {
  return mount(StatCard, {
    props: { icon: 'pi pi-inbox', title: 'Bu ayki hızlı talepler', ...props },
    global: { plugins: [PrimeVue] },
  })
}

describe('StatCard', () => {
  it('başlığı, biçimlenmiş değeri ve aynı ikonun filigranını gösterir', () => {
    const wrapper = mountCard({ value: 1250, note: 'Bilgi' })

    expect(wrapper.get('.stat-card__title').text()).toBe('Bu ayki hızlı talepler')
    expect(wrapper.get('.stat-card__value').text()).toBe('1.250')
    expect(wrapper.get('.stat-card__watermark').classes()).toContain('pi-inbox')
    expect(wrapper.get('.stat-card__watermark').attributes('aria-hidden')).toBe('true')
  })

  it('artışı yukarı okla ve ekran okuyucu için sözcükle gösterir', () => {
    const wrapper = mountCard({ value: 10, change: 25 })

    const trend = wrapper.get('.stat-card__trend')
    expect(trend.classes()).toContain('stat-card__trend--up')
    expect(trend.text()).toContain('▲')
    expect(trend.text()).toContain('artış')
    expect(wrapper.get('.stat-card__foot').text()).toContain('%25')
    expect(wrapper.get('.stat-card__foot').text()).toContain('geçen aya göre')
  })

  it('azalışı aşağı okla gösterir', () => {
    const wrapper = mountCard({ value: 10, change: -20 })

    expect(wrapper.get('.stat-card__trend').classes()).toContain('stat-card__trend--down')
    expect(wrapper.get('.stat-card__trend').text()).toContain('▼')
  })

  it('önceki dönemde veri yoksa yüzde yerine açıklama gösterir', () => {
    const wrapper = mountCard({ value: 4, change: null })

    expect(wrapper.find('.stat-card__trend').exists()).toBe(false)
    expect(wrapper.get('.stat-card__foot').text()).toBe('Geçen ay aynı dönemde kayıt yoktu')
  })

  it('kıyas verilmediğinde alt satırda notu gösterir', () => {
    const wrapper = mountCard({ value: 6, note: 'En çok talep: Evde bakım' })

    expect(wrapper.get('.stat-card__foot').text()).toBe('En çok talep: Evde bakım')
  })

  it('yüklenirken değer yerine iskelet gösterir', () => {
    const wrapper = mountCard({ value: null, loading: true })

    expect(wrapper.find('.stat-card__value .p-skeleton').exists()).toBe(true)
  })
})
