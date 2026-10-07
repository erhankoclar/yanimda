import { describe, expect, it } from 'vitest'

import { isValidPhone, stepOfFields, validateStep } from '@/utils/requestValidation'

const TODAY = new Date(2026, 9, 7)

const valid = {
  service: 1,
  elder_full_name: 'Fatma Yılmaz',
  elder_age: '78',
  relationship: 'parent',
  preferred_date: '2026-10-10',
  time_slot: 'morning',
  city: 'Samsun',
  district: 'İlkadım',
  address: 'Örnek Mah. No: 1',
  contact_phone: '0555 111 22 33',
  alternate_contact_name: '',
  alternate_contact_phone: '',
  consent: true,
}

describe('validateStep', () => {
  it('geçerli formda hiçbir adım hata vermez', () => {
    ;[0, 1, 2, 3, 4].forEach((step) => expect(validateStep(step, valid, TODAY), `adım ${step}`).toEqual({}))
  })

  it('hizmet seçilmeden ilk adım geçilemez', () => {
    expect(validateStep(0, { ...valid, service: null }, TODAY)).toHaveProperty('service')
  })

  it.each([['39', true], ['40', false], ['120', false], ['121', true], ['78.5', true], ['abc', true]])(
    'yaş %s için hata=%s',
    (age, hasError) => {
      expect('elder_age' in validateStep(1, { ...valid, elder_age: age }, TODAY)).toBe(hasError)
    },
  )

  it.each([
    ['2026-10-06', true],
    ['2026-10-07', false],
    ['2027-01-05', false],
    ['2027-01-06', true],
  ])('tarih %s için hata=%s (bugün ve 90 gün sınırı)', (date, hasError) => {
    expect('preferred_date' in validateStep(2, { ...valid, preferred_date: date }, TODAY)).toBe(hasError)
  })

  it('adres alanları boş bırakılamaz', () => {
    const errors = validateStep(2, { ...valid, city: ' ', district: '', address: '' }, TODAY)

    expect(Object.keys(errors).sort()).toEqual(['address', 'city', 'district'])
  })

  it('ikinci kişinin adı ve telefonu birlikte istenir', () => {
    expect(validateStep(3, { ...valid, alternate_contact_name: 'Mehmet' }, TODAY)).toHaveProperty('alternate_contact_phone')
    expect(validateStep(3, { ...valid, alternate_contact_phone: '05550001122' }, TODAY)).toHaveProperty('alternate_contact_name')
  })

  it('onay verilmeden gönderilemez', () => {
    expect(validateStep(4, { ...valid, consent: false }, TODAY)).toHaveProperty('consent')
  })
})

describe('isValidPhone', () => {
  it.each([
    ['0555 111 22 33', true],
    ['+90 (555) 111-22-33', true],
    ['555111223', false],
    ['0555abc1122', false],
    ['1234567890123456', false],
  ])('%s → %s', (phone, expected) => {
    expect(isValidPhone(phone)).toBe(expected)
  })
})

describe('stepOfFields', () => {
  it('sunucu hatasının ait olduğu ilk adımı bulur', () => {
    expect(stepOfFields({ contact_phone: 'x', city: 'y' })).toBe(2)
    expect(stepOfFields({ service: 'mükerrer' })).toBe(0)
    expect(stepOfFields({ bilinmeyen: 'x' })).toBe(4)
  })
})
