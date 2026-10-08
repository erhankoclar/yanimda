import { afterEach, describe, expect, it } from 'vitest'

import { changeInfo, formatNumber } from '@/admin/format'
import { i18n } from '@/i18n'

afterEach(() => {
  i18n.global.locale.value = 'tr'
})

describe('admin sayı biçimleri', () => {
  it('sayıyı etkin dilin binlik ayracıyla yazar', () => {
    expect(formatNumber(1250)).toBe('1.250')

    i18n.global.locale.value = 'en'

    expect(formatNumber(1250)).toBe('1,250')
  })

  it('artış ve azalışı yön ve işaretsiz yüzde olarak verir', () => {
    expect(changeInfo(25)).toEqual({ trend: 'up', text: '%25' })
    expect(changeInfo(-20)).toEqual({ trend: 'down', text: '%20' })

    i18n.global.locale.value = 'en'

    expect(changeInfo(25).text).toBe('25%')
  })

  it('değişim yoksa düz, önceki dönem boşsa kıyassız sonuç verir', () => {
    expect(changeInfo(0)).toEqual({ trend: 'flat', text: '%0' })
    expect(changeInfo(null)).toEqual({ trend: 'none', text: '' })
  })
})
