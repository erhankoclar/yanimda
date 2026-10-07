// Backend'deki CareRequest seçenekleriyle aynı değerler; etiketler arayüz dilindedir.

export const RELATIONSHIP_OPTIONS = [
  { value: 'parent', label: 'Annem / babam' },
  { value: 'grandparent', label: 'Büyükannem / büyükbabam' },
  { value: 'relative', label: 'Diğer akrabam' },
  { value: 'neighbor', label: 'Komşum / dostum' },
  { value: 'self', label: 'Kendim' },
]

export const TIME_SLOT_OPTIONS = [
  { value: 'morning', label: 'Sabah (08:00-12:00)' },
  { value: 'afternoon', label: 'Öğleden sonra (12:00-17:00)' },
  { value: 'evening', label: 'Akşam (17:00-21:00)' },
]

export const STATUS_LABELS = {
  new: 'Alındı',
  reviewing: 'İnceleniyor',
  assigned: 'Kişi atandı',
  completed: 'Tamamlandı',
  cancelled: 'İptal edildi',
}

export const MIN_ELDER_AGE = 40
export const MAX_ELDER_AGE = 120
export const MAX_PREFERRED_DAYS_AHEAD = 90

/**
 * Seçenek listesinde değerin etiketini bulur.
 *
 * @param {Array<{ value: string, label: string }>} options Seçenekler.
 * @param {string} value Değer.
 * @returns {string} Etiket; bulunamazsa değerin kendisi.
 */
export function optionLabel(options, value) {
  return options.find((option) => option.value === value)?.label ?? value
}
