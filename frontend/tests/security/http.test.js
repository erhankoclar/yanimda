import { afterEach, describe, expect, it, vi } from 'vitest'

import { http, onSessionExpired } from '@/api/http'
import { tokenStorage } from '@/api/tokenStorage'

import { restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'

afterEach(() => {
  restoreApi()
  window.localStorage.clear()
})

describe('http istemcisi güvenliği', () => {
  it.each([
    'https://evil.example/collect',
    '//evil.example/collect',
  ])('token’ı dış adrese göndermez: %s', async (url) => {
    tokenStorage.set({ access: 'gizli', refresh: 'r1' })
    const calls = useFakeApi(() => [200, {}])

    await http.get(url)

    expect(calls[0].headers.Authorization).toBeUndefined()
  })

  it('yenileme başarısız olursa token’ları siler ve oturum düştü bildirimi yapar', async () => {
    tokenStorage.set({ access: 'eski', refresh: 'gecersiz' })
    const listener = vi.fn()
    const unsubscribe = onSessionExpired(listener)
    useFakeApi(routeHandler({
      'GET /auth/me/': () => [401, {}],
      'POST /auth/token/refresh/': () => [401, { detail: 'Token is invalid' }],
    }))

    await expect(http.get('/auth/me/')).rejects.toBeTruthy()

    expect(tokenStorage.getAccess()).toBeNull()
    expect(tokenStorage.getRefresh()).toBeNull()
    expect(listener).toHaveBeenCalledTimes(1)
    unsubscribe()
  })

  it('giriş isteğindeki 401’de yenileme denemez', async () => {
    tokenStorage.set({ access: 'eski', refresh: 'r1' })
    const calls = useFakeApi(() => [401, {}])

    await expect(http.post('/auth/token/', {}, { skipAuthRefresh: true })).rejects.toBeTruthy()

    expect(calls).toHaveLength(1)
  })
})
