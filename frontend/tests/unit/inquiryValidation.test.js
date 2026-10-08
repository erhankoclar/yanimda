import { describe, expect, it } from 'vitest'

import { validateInquiry } from '@/utils/inquiryValidation'

const valid = {
  full_name: 'Deneme Kişi',
  email: 'deneme@example.com',
  service: 3,
  district: 5,
  neighborhood: 11,
  message: 'Annem için refakat desteği istiyoruz.',
  consent: true,
}

describe('validateInquiry', () => {
  it('geçerli formda hata vermez', () => {
    expect(validateInquiry(valid)).toEqual({})
  })

  it('boş formda tüm zorunlu alanları işaretler', () => {
    const errors = validateInquiry({ full_name: '', email: '', service: '', district: '', neighborhood: '', message: '', consent: false })

    expect(Object.keys(errors).sort()).toEqual(['consent', 'district', 'email', 'full_name', 'message', 'service'])
  })

  it('ilçe seçilmeden mahalle yerine ilçe hatası verir', () => {
    expect(validateInquiry({ ...valid, district: '', neighborhood: '' })).toHaveProperty('district')
  })

  it('ilçe seçili ama mahalle seçilmemişse mahalle hatası verir', () => {
    const errors = validateInquiry({ ...valid, neighborhood: '' })

    expect(Object.keys(errors)).toEqual(['neighborhood'])
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
