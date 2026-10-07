import { afterEach, describe, expect, it } from 'vitest'

import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

describe('yönlendirme', () => {
  it('ana sayfayı son kullanıcı layout’u içinde açar', async () => {
    ;({ wrapper } = await mountApp('/'))

    expect(wrapper.find('[data-layout="public"]').exists()).toBe(true)
    expect(wrapper.find('[data-layout="admin"]').exists()).toBe(false)
    expect(wrapper.get('h1').text()).toContain('yanınızdayız')
  })

  it('/admin adresini gösterge paneline yönlendirir ve admin layout’unu kullanır', async () => {
    const mounted = await mountApp('/admin')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('admin-dashboard')
    expect(wrapper.find('[data-layout="admin"]').exists()).toBe(true)
    expect(wrapper.find('[data-layout="public"]').exists()).toBe(false)
  })

  it('admin giriş sayfasını iki layout’un da dışında açar', async () => {
    ;({ wrapper } = await mountApp('/admin/login'))

    expect(wrapper.find('[data-layout]').exists()).toBe(false)
    expect(wrapper.get('h1').text()).toBe('Yönetici girişi')
  })

  it('bilinmeyen adreste bulunamadı sayfasını gösterir', async () => {
    ;({ wrapper } = await mountApp('/olmayan/sayfa'))

    expect(wrapper.get('h1').text()).toBe('Sayfa bulunamadı')
  })

  it('sayısal olmayan talep kimliğini bulunamadı sayfasına düşürür', async () => {
    const mounted = await mountApp('/requests/abc')
    wrapper = mounted.wrapper

    expect(mounted.router.currentRoute.value.name).toBe('not-found')
  })
})
