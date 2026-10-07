import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

describe('giriş sonrası yönlendirme güvenliği', () => {
  it.each(['//evil.example', 'https://evil.example/phish'])(
    'redirect parametresindeki dış adrese (%s) gitmez, başvurulara döner',
    async (target) => {
      useFakeApi(routeHandler({
        'POST /auth/token/': () => [200, { access: 'a1', refresh: 'r1' }],
        'GET /auth/me/': () => [200, APPLICANT],
      }))
      const mounted = await mountApp(`/login?redirect=${encodeURIComponent(target)}`)
      wrapper = mounted.wrapper
      const inputs = wrapper.findAll('input')

      await inputs[0].setValue('ayse@example.com')
      await inputs[1].setValue('Yanimda-Guclu-2026')
      await wrapper.get('form').trigger('submit')
      await flushPromises()

      await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/requests'))
    },
  )

  it('parola alanı tarayıcı tarafından düz metin olarak gösterilmez ve otomatik doldurma ipucu taşır', async () => {
    ;({ wrapper } = await mountApp('/login'))

    const password = wrapper.get('input[type="password"]')
    expect(password.attributes('autocomplete')).toBe('current-password')
  })
})
