import { describe, expect, it } from 'vitest'

import { safeRedirect } from '@/utils/safeRedirect'

describe('safeRedirect', () => {
  it('uygulama içi yolları olduğu gibi döndürür', () => {
    expect(safeRedirect('/requests/5?tab=1', '/')).toBe('/requests/5?tab=1')
  })

  it('metin olmayan veya boş değerlerde varsayılanı döndürür', () => {
    expect(safeRedirect(undefined, '/x')).toBe('/x')
    expect(safeRedirect(['/a'], '/x')).toBe('/x')
    expect(safeRedirect('', '/x')).toBe('/x')
  })
})
