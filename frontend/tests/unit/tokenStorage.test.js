import { afterEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

afterEach(() => window.localStorage.clear())

describe('tokenStorage', () => {
  it('token çiftini kaydeder ve okur', () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })

    expect(tokenStorage.getAccess()).toBe('a1')
    expect(tokenStorage.getRefresh()).toBe('r1')
  })

  it('yalnızca access verildiğinde mevcut refresh token’ı korur', () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })

    tokenStorage.set({ access: 'a2' })

    expect(tokenStorage.getAccess()).toBe('a2')
    expect(tokenStorage.getRefresh()).toBe('r1')
  })

  it('clear ile iki token’ı da siler', () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })

    tokenStorage.clear()

    expect(tokenStorage.getAccess()).toBeNull()
    expect(tokenStorage.getRefresh()).toBeNull()
  })

  it('depolama erişilemezse hata fırlatmaz ve null döner', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => { throw new Error('blocked') })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('blocked') })

    expect(() => tokenStorage.set({ access: 'a', refresh: 'r' })).not.toThrow()
    expect(tokenStorage.getAccess()).toBeNull()
  })
})
