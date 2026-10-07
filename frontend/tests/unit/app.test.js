import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import App from '@/App.vue'

describe('App', () => {
  it('uygulama başlığını gösterir', () => {
    const wrapper = mount(App)

    expect(wrapper.get('h1').text()).toBe('Yanımda')
  })
})
