import { afterEach, describe, expect, it } from 'vitest'

import { http } from '@/api/http'
import { tokenStorage } from '@/api/tokenStorage'

import { restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'

afterEach(() => {
  restoreApi()
  window.localStorage.clear()
})

describe('http istemcisi', () => {
  it('API isteklerine Bearer token ekler', async () => {
    tokenStorage.set({ access: 'erisim', refresh: 'yenileme' })
    const calls = useFakeApi(() => [200, {}])

    await http.get('/services/')

    expect(calls[0].headers.Authorization).toBe('Bearer erisim')
  })

  it('401 alınca token’ı yenileyip isteği bir kez tekrarlar', async () => {
    tokenStorage.set({ access: 'eski', refresh: 'r1' })
    const calls = useFakeApi(routeHandler({
      'GET /auth/me/': (config) => (config.headers.Authorization === 'Bearer yeni' ? [200, { id: 1 }] : [401, {}]),
      'POST /auth/token/refresh/': () => [200, { access: 'yeni', refresh: 'r2' }],
    }))

    const response = await http.get('/auth/me/')

    expect(response.data).toEqual({ id: 1 })
    expect(calls.map((call) => call.url)).toEqual(['/auth/me/', '/auth/token/refresh/', '/auth/me/'])
    expect(tokenStorage.getAccess()).toBe('yeni')
    expect(tokenStorage.getRefresh()).toBe('r2')
  })

  it('eşzamanlı 401’lerde tek yenileme isteği yapar', async () => {
    tokenStorage.set({ access: 'eski', refresh: 'r1' })
    const calls = useFakeApi(routeHandler({
      'GET /a/': (config) => (config.headers.Authorization === 'Bearer yeni' ? [200, 'a'] : [401, {}]),
      'GET /b/': (config) => (config.headers.Authorization === 'Bearer yeni' ? [200, 'b'] : [401, {}]),
      'POST /auth/token/refresh/': () => [200, { access: 'yeni' }],
    }))

    const results = await Promise.all([http.get('/a/'), http.get('/b/')])

    expect(results.map((response) => response.data)).toEqual(['a', 'b'])
    expect(calls.filter((call) => call.url === '/auth/token/refresh/')).toHaveLength(1)
  })

  it('tekrar denenen istek yine 401 alırsa sonsuz döngüye girmez', async () => {
    tokenStorage.set({ access: 'eski', refresh: 'r1' })
    const calls = useFakeApi(routeHandler({
      'GET /auth/me/': () => [401, {}],
      'POST /auth/token/refresh/': () => [200, { access: 'yeni' }],
    }))

    await expect(http.get('/auth/me/')).rejects.toMatchObject({ response: { status: 401 } })
    expect(calls).toHaveLength(3)
  })
})
