import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { APPLICANT, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

afterEach(() => wrapper?.unmount())

/**
 * Etiketi verilen alanı bulup değer yazar.
 *
 * @param {import('@vue/test-utils').VueWrapper} root Kök bileşen.
 * @param {string} label Alan etiketinin başlangıcı.
 * @param {string} value Yazılacak değer.
 */
async function fill(root, label, value) {
  const labelEl = root.findAll('label').find((item) => item.text().startsWith(label))
  await root.get(`#${labelEl.attributes('for')}`).setValue(value)
}

/** Formu gönderir ve bekleyen işleri tamamlar. */
async function submit(root) {
  await root.get('form').trigger('submit')
  await flushPromises()
}

describe('giriş sayfası', () => {
  it('boş gönderimde alan hatalarını gösterir ve istek yapmaz', async () => {
    const calls = useFakeApi(() => [200, []])
    ;({ wrapper } = await mountApp('/login'))

    await submit(wrapper)

    expect(wrapper.text()).toContain('E-posta adresinizi yazın.')
    expect(wrapper.text()).toContain('Parolanızı yazın.')
    expect(calls.filter((call) => call.url === '/auth/token/')).toHaveLength(0)
  })

  it('hatalı bilgilerde anlaşılır genel hata gösterir', async () => {
    useFakeApi(routeHandler({ 'POST /auth/token/': () => [401, { detail: 'No active account' }] }))
    ;({ wrapper } = await mountApp('/login'))

    await fill(wrapper, 'E-posta', 'ayse@example.com')
    await fill(wrapper, 'Parola', 'yanlis')
    await submit(wrapper)

    expect(wrapper.get('[role="alert"]').text()).toContain('E-posta adresi veya parola hatalı')
  })

  it('başarılı girişte geldiği sayfaya döner', async () => {
    useFakeApi(routeHandler({
      'POST /auth/token/': () => [200, { access: 'a1', refresh: 'r1' }],
      'GET /auth/me/': () => [200, APPLICANT],
    }))
    const mounted = await mountApp('/login?redirect=/requests/new')
    wrapper = mounted.wrapper

    await fill(wrapper, 'E-posta', 'ayse@example.com')
    await fill(wrapper, 'Parola', 'Yanimda-Guclu-2026')
    await submit(wrapper)

    await vi.waitFor(() => expect(mounted.router.currentRoute.value.fullPath).toBe('/requests/new'), { timeout: 5000 })
    expect(tokenStorage.getAccess()).toBe('a1')
  })

  it('kayıt bağlantısı dönüş adresini korur', async () => {
    ;({ wrapper } = await mountApp('/login?redirect=/requests/new'))

    const link = wrapper.findAll('a').find((item) => item.text() === 'Kayıt olun')
    expect(link.attributes('href')).toBe('/register?redirect=/requests/new')
  })
})

describe('kayıt sayfası', () => {
  it('kısa parolayı göndermeden önce uyarır', async () => {
    const calls = useFakeApi(() => [200, []])
    ;({ wrapper } = await mountApp('/register'))

    await fill(wrapper, 'Adınız', 'Ayşe')
    await fill(wrapper, 'Soyadınız', 'Yılmaz')
    await fill(wrapper, 'E-posta', 'ayse@example.com')
    await fill(wrapper, 'Parola', 'kisa')
    await submit(wrapper)

    expect(wrapper.text()).toContain('en az 8 karakter')
    expect(calls.filter((call) => call.url === '/auth/register/')).toHaveLength(0)
  })

  it('sunucunun alan hatasını ilgili alanın altında gösterir', async () => {
    useFakeApi(routeHandler({
      'POST /auth/register/': () => [400, { email: ['Bu e-posta adresiyle kayıtlı bir kullanıcı zaten var.'] }],
    }))
    ;({ wrapper } = await mountApp('/register'))

    await fill(wrapper, 'Adınız', 'Ayşe')
    await fill(wrapper, 'Soyadınız', 'Yılmaz')
    await fill(wrapper, 'E-posta', 'ayse@example.com')
    await fill(wrapper, 'Parola', 'Yanimda-Guclu-2026')
    await submit(wrapper)

    const emailInput = wrapper.findAll('input').find((input) => input.attributes('type') === 'email')
    expect(emailInput.attributes('aria-invalid')).toBe('true')
    expect(wrapper.text()).toContain('zaten var')
  })

  it('kayıt olunca oturum açar ve başvuru sayfasına gider', async () => {
    const calls = useFakeApi(routeHandler({
      'POST /auth/register/': () => [201, { id: 1 }],
      'POST /auth/token/': () => [200, { access: 'a1', refresh: 'r1' }],
      'GET /auth/me/': () => [200, APPLICANT],
    }))
    const mounted = await mountApp('/register')
    wrapper = mounted.wrapper

    await fill(wrapper, 'Adınız', 'Ayşe')
    await fill(wrapper, 'Soyadınız', 'Yılmaz')
    await fill(wrapper, 'E-posta', ' ayse@example.com ')
    await fill(wrapper, 'Telefon', '0555 111 22 33')
    await fill(wrapper, 'Parola', 'Yanimda-Guclu-2026')
    await submit(wrapper)

    const sent = JSON.parse(calls.find((call) => call.url === '/auth/register/').data)
    expect(sent).toMatchObject({ email: 'ayse@example.com', first_name: 'Ayşe', phone: '0555 111 22 33' })
    await vi.waitFor(() => expect(mounted.router.currentRoute.value.name).toBe('request-new'), { timeout: 5000 })
  })

  it('parolayı göster seçeneği alan tipini değiştirir', async () => {
    ;({ wrapper } = await mountApp('/register'))
    const passwordField = () => wrapper.findAll('input').find((input) => input.attributes('autocomplete') === 'new-password')

    expect(passwordField().attributes('type')).toBe('password')
    await wrapper.get('input[type="checkbox"]').setValue(true)

    expect(passwordField().attributes('type')).toBe('text')
  })
})
