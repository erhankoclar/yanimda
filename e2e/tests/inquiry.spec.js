import { expect, test } from '@playwright/test'

import { adminToken, uniqueEmail } from './helpers.js'

test.describe('hızlı talep formu', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/#talep-formu')
    await expect(page.locator('#talep-formu select option')).not.toHaveCount(1)
  })

  test('boş gönderimde istemci doğrulaması alanları işaretler ve istek yapmaz', async ({ page }) => {
    let posted = false
    page.on('request', (request) => { if (request.url().endsWith('/api/inquiries/')) posted = true })
    const form = page.locator('#talep-formu')

    await form.getByRole('button', { name: 'Talebimi gönder' }).click()

    await expect(form.getByText('Adınızı ve soyadınızı yazın.')).toBeVisible()
    await expect(form.getByText('E-posta adresinizi yazın.')).toBeVisible()
    await expect(form.getByText('Bir hizmet seçin.')).toBeVisible()
    expect(posted).toBe(false)
  })

  test('geçerli talep "Gönderiliyor…" durumundan geçip kaydedilir ve kayıt veritabanında bulunur', async ({ page, request }) => {
    const email = uniqueEmail('e2e.talep')
    const form = page.locator('#talep-formu')
    await form.getByLabel('Adınız ve soyadınız').fill('Deneme Kişi')
    await form.getByLabel('E-posta adresiniz').fill(email)
    await form.getByLabel('Hangi hizmet?').selectOption({ index: 1 })
    await form.getByLabel('Kısaca anlatın').fill('Kurgusal test: annem için haftada iki gün refakat.')
    await form.getByRole('checkbox').check()
    // Gönderim durumunu görebilmek için istek yapay olarak geciktirilir.
    await page.route('**/api/inquiries/', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 800))
      await route.continue()
    })

    await form.getByRole('button', { name: 'Talebimi gönder' }).click()

    await expect(form.getByRole('button', { name: 'Gönderiliyor…' })).toBeDisabled()
    await expect(form.getByText('Talebiniz alındı')).toBeVisible()
    const recordId = (await form.locator('.inquiry__success strong').textContent()).replace('#', '')

    const token = await adminToken(request)
    const stored = await (await request.get(`/api/admin/inquiries/?search=${encodeURIComponent(email)}`, {
      headers: { Authorization: `Bearer ${token}` },
    })).json()
    expect(stored.results).toHaveLength(1)
    expect(String(stored.results[0].id)).toBe(recordId)
    expect(stored.results[0].email).toBe(email)
  })

  test('sunucu hata verirse başarı mesajı gösterilmez ve yazılanlar korunur', async ({ page }) => {
    const form = page.locator('#talep-formu')
    await form.getByLabel('Adınız ve soyadınız').fill('Deneme Kişi')
    await form.getByLabel('E-posta adresiniz').fill(uniqueEmail('e2e.hata'))
    await form.getByLabel('Hangi hizmet?').selectOption({ index: 1 })
    await form.getByLabel('Kısaca anlatın').fill('Kurgusal test: sunucu hatası durumu.')
    await form.getByRole('checkbox').check()
    await page.route('**/api/inquiries/', (route) => route.fulfill({ status: 500, body: 'hata' }))

    await form.getByRole('button', { name: 'Talebimi gönder' }).click()

    await expect(form.getByRole('alert').first()).toContainText('Beklenmeyen bir sorun')
    await expect(form.getByText('Talebiniz alındı')).toHaveCount(0)
    await expect(form.getByLabel('Kısaca anlatın')).toHaveValue('Kurgusal test: sunucu hatası durumu.')
  })

  test('sunucu tarafı doğrulama, istemci atlatılsa bile geçersiz kaydı reddeder', async ({ request }) => {
    const response = await request.post('/api/inquiries/', {
      data: { full_name: 'A', email: 'gecersiz', service: 999999, message: 'kısa', consent: false },
    })

    expect(response.status()).toBe(400)
    const body = await response.json()
    expect(Object.keys(body).sort()).toEqual(['consent', 'email', 'full_name', 'message', 'service'])
  })
})
