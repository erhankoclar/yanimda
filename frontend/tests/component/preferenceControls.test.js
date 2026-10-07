import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it } from 'vitest'

import PreferenceControls from '@/components/common/PreferenceControls.vue'

/**
 * Tercih kontrollerini yeni bir Pinia ile bağlar.
 *
 * @returns {import('@vue/test-utils').VueWrapper} Bağlanmış bileşen.
 */
function mountControls() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(PreferenceControls, { global: { plugins: [pinia] } })
}

describe('PreferenceControls', () => {
  it('bayrak düğmeleri seçili dili aria-pressed ile bildirir ve dili değiştirir', async () => {
    const wrapper = mountControls()
    const [turkish, english] = wrapper.findAll('[lang]')

    expect(turkish.attributes('aria-pressed')).toBe('true')
    expect(english.attributes('aria-pressed')).toBe('false')

    await english.trigger('click')

    expect(english.attributes('aria-pressed')).toBe('true')
    expect(document.documentElement.lang).toBe('en')
    // Etiketler de seçilen dile geçer.
    expect(english.attributes('aria-label')).toBe('Switch to English')
  })

  it('tema düğmesi temayı değiştirir ve etiketi yeni duruma göre günceller', async () => {
    window.localStorage.setItem('yanimda.theme', 'light')
    const wrapper = mountControls()
    const toggle = wrapper.find('.preference-controls__theme')

    expect(toggle.attributes('aria-label')).toBe('Koyu temaya geç')

    await toggle.trigger('click')

    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(toggle.attributes('aria-label')).toBe('Açık temaya geç')
  })
})
