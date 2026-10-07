import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'
import { useAuthStore } from '@/stores/auth'

import { ADMIN, APPLICANT, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => {
  restoreApi()
  window.localStorage.clear()
})

describe('auth store', () => {
  it('giriş yapınca token’ları saklar ve kullanıcıyı yükler', async () => {
    const calls = useFakeApi(routeHandler({
      'POST /auth/token/': () => [200, { access: 'a1', refresh: 'r1' }],
      'GET /auth/me/': () => [200, APPLICANT],
    }))
    const auth = useAuthStore()

    await auth.login(' ayse@example.com ', 'parola')

    expect(JSON.parse(calls[0].data).email).toBe('ayse@example.com')
    expect(tokenStorage.getAccess()).toBe('a1')
    expect(auth.isAuthenticated).toBe(true)
    expect(auth.isAdmin).toBe(false)
    expect(auth.displayName).toBe('Ayşe Yılmaz')
  })

  it('kayıt olduktan sonra aynı bilgilerle giriş yapar', async () => {
    const calls = useFakeApi(routeHandler({
      'POST /auth/register/': () => [201, { id: 1 }],
      'POST /auth/token/': () => [200, { access: 'a1', refresh: 'r1' }],
      'GET /auth/me/': () => [200, APPLICANT],
    }))
    const auth = useAuthStore()

    await auth.register({ email: 'ayse@example.com', password: 'p', first_name: 'Ayşe', last_name: 'Yılmaz' })

    expect(calls.map((call) => call.url)).toEqual(['/auth/register/', '/auth/token/', '/auth/me/'])
    expect(auth.isAuthenticated).toBe(true)
  })

  it('saklı token varsa açılışta kullanıcıyı bir kez yükler', async () => {
    tokenStorage.set({ access: 'a1', refresh: 'r1' })
    const calls = useFakeApi(routeHandler({ 'GET /auth/me/': () => [200, ADMIN] }))
    const auth = useAuthStore()

    await Promise.all([auth.init(), auth.init()])

    expect(calls).toHaveLength(1)
    expect(auth.isAdmin).toBe(true)
    expect(auth.initialized).toBe(true)
  })

  it('token yoksa açılışta istek yapmaz', async () => {
    const calls = useFakeApi(() => [200, {}])
    const auth = useAuthStore()

    await auth.init()

    expect(calls).toHaveLength(0)
    expect(auth.isAuthenticated).toBe(false)
  })

  it('geçersiz saklı token ile açılışta oturumu temizler', async () => {
    tokenStorage.set({ access: 'bozuk' })
    useFakeApi(routeHandler({ 'GET /auth/me/': () => [401, {}] }))
    const auth = useAuthStore()

    await auth.init()

    expect(auth.isAuthenticated).toBe(false)
    expect(tokenStorage.getAccess()).toBeNull()
  })

  it('çıkış yapınca kullanıcıyı ve token’ları temizler', async () => {
    useFakeApi(routeHandler({
      'POST /auth/token/': () => [200, { access: 'a1', refresh: 'r1' }],
      'GET /auth/me/': () => [200, APPLICANT],
    }))
    const auth = useAuthStore()
    await auth.login('ayse@example.com', 'parola')

    auth.logout()

    expect(auth.isAuthenticated).toBe(false)
    expect(tokenStorage.getRefresh()).toBeNull()
  })
})
