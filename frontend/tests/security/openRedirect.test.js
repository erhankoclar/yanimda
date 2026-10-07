import { describe, expect, it } from 'vitest'

import { safeRedirect } from '@/utils/safeRedirect'

describe('açık yönlendirme koruması', () => {
  it.each([
    'https://evil.example',
    '//evil.example',
    '/\\evil.example',
    'javascript:alert(1)',
    'evil.example/path',
  ])('dış veya tehlikeli adresi reddeder: %s', (value) => {
    expect(safeRedirect(value, '/')).toBe('/')
  })
})
