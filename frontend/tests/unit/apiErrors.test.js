import { describe, expect, it } from 'vitest'

import { parseApiError } from '@/utils/apiErrors'

const response = (status, data) => ({ response: { status, data } })

describe('parseApiError', () => {
  it('DRF alan hatalarını ilgili alanlara, diğerlerini genel mesaja yazar', () => {
    const result = parseApiError(
      response(400, { email: ['Bu e-posta kayıtlı.'], non_field_errors: ['Genel sorun.'] }),
      ['email'],
    )

    expect(result).toEqual({ fields: { email: 'Bu e-posta kayıtlı.' }, general: 'Genel sorun.' })
  })

  it('formda olmayan alanın hatasını kaybetmez, genel mesaja ekler', () => {
    const result = parseApiError(response(400, { service: ['Açık başvurunuz var.'] }), ['email'])

    expect(result.general).toBe('Açık başvurunuz var.')
  })

  it('detail mesajını genel mesaj yapar', () => {
    expect(parseApiError(response(403, { detail: 'Yetkiniz yok.' })).general).toBe('Yetkiniz yok.')
  })

  it.each([
    [{}, 'Sunucuya ulaşılamadı'],
    [response(429, {}), 'Çok fazla deneme'],
    [response(502, '<html>'), 'Beklenmeyen bir sorun'],
    [response(400, {}), 'İşlem tamamlanamadı'],
  ])('özel durumlarda yol gösteren mesaj verir', (error, expected) => {
    expect(parseApiError(error).general).toContain(expected)
  })
})
