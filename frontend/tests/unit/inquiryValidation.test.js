import { describe, expect, it } from 'vitest'

import { validateInquiry } from '@/utils/inquiryValidation'

const valid = {
  full_name: 'Deneme Kişi',
  email: 'deneme@example.com',
  service: 3,
  message: 'Annem için refakat desteği istiyoruz.',
  consent: true,
}

describe('validateInquiry', () => {
  it('geçerli formda hata vermez', () => {
    expect(validateInquiry(valid)).toEqual({})
  })

  it('boş formda tüm zorunlu alanları işaretler', () => {
    const errors = validateInquiry({ full_name: '', email: '', service: '', message: '', consent: false })

    expect(Object.keys(errors).sort()).toEqual(['consent', 'email', 'full_name', 'message', 'service'])
  })

  it.each(['deneme', 'deneme@', 'deneme@example', 'a b@example.com'])('geçersiz e-postayı reddeder: %s', (email) => {
    expect(validateInquiry({ ...valid, email })).toHaveProperty('email')
  })

  it.each([
    ['123456789', true],
    ['1234567890', false],
    ['a'.repeat(2000), false],
    ['a'.repeat(2001), true],
  ])('açıklama uzunluğu %#: hata=%s', (message, hasError) => {
    expect('message' in validateInquiry({ ...valid, message })).toBe(hasError)
  })

  it('yalnızca boşluktan oluşan adı reddeder', () => {
    expect(validateInquiry({ ...valid, full_name: '   A  ' })).toHaveProperty('full_name')
  })
})
