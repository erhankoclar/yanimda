import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'

import { createAppRouter } from '@/router'

describe('admin detay route’ları', () => {
  // Kimlik düzenindeki ters eğik çizgi tekleşince `\d+` yerine `d+` aranıyor,
  // detay sayfaları bulunamadı sayfasına düşüyordu.
  it.each([
    ['/admin/requests/7', 'admin-request-detail'],
    ['/admin/users/12', 'admin-user-detail'],
  ])('%s sayısal kimlikle %s sayfasına çözülür', (path, name) => {
    const router = createAppRouter({ pinia: createPinia(), memory: true })

    expect(router.resolve(path).name).toBe(name)
  })

  it('sayısal olmayan kimlik detay sayfasına çözülmez', () => {
    const router = createAppRouter({ pinia: createPinia(), memory: true })

    expect(router.resolve('/admin/requests/abc').name).not.toBe('admin-request-detail')
  })
})
