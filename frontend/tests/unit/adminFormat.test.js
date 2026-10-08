import { afterEach, describe, expect, it } from 'vitest'

import { changeInfo, formatNumber, formatRelativeTime, formatShortDate } from '@/admin/format'
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

  it('tarihi kısa gün-ay biçiminde yazar', () => {
    expect(formatShortDate('2026-10-06')).toBe('6 Eki')

    i18n.global.locale.value = 'en'

    expect(formatShortDate('2026-10-06')).toBe('6 Oct')
  })

  it('zamanı şimdiye göre dakika, saat ve gün olarak yazar', () => {
    const now = new Date('2026-10-08T12:00:00Z')

    expect(formatRelativeTime('2026-10-08T11:59:30Z', now)).toBe('şimdi')
    expect(formatRelativeTime('2026-10-08T11:48:00Z', now)).toBe('12 dakika önce')
    expect(formatRelativeTime('2026-10-08T09:00:00Z', now)).toBe('3 saat önce')
    expect(formatRelativeTime('2026-10-03T12:00:00Z', now)).toBe('5 gün önce')

    i18n.global.locale.value = 'en'

    expect(formatRelativeTime('2026-10-08T11:48:00Z', now)).toBe('12 minutes ago')
  })
})
