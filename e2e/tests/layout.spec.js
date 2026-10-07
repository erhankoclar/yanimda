import { expect, test } from '@playwright/test'

const PAGES = ['/', '/login', '/register']

// Üretim imajı yerelde düz HTTP üzerinden denenirken tarayıcı, Django'nun gönderdiği
// Cross-Origin-Opener-Policy başlığını yok saydığını bildirir. HTTPS'te (Render) bu uyarı oluşmaz.
const IGNORED_CONSOLE = ['Cross-Origin-Opener-Policy header has been ignored']

test.describe('duyarlı düzen', () => {
  for (const path of PAGES) {
    test(`${path} yatay kaydırma oluşturmaz ve konsol hatası vermez`, async ({ page }) => {
      const errors = []
      page.on('pageerror', (error) => errors.push(error.message))
      page.on('console', (message) => {
        const ignored = IGNORED_CONSOLE.some((text) => message.text().includes(text))
        if (message.type() === 'error' && !ignored) errors.push(message.text())
      })

      await page.goto(path)
      await expect(page.locator('h1')).toBeVisible()

      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      expect(overflow).toBeLessThanOrEqual(0)
      expect(errors).toEqual([])
    })
  }

  test('ana sayfa hizmetleri, talep formunu ve sık sorulanları gösterir', async ({ page }) => {
    await page.goto('/')

    await expect(page.locator('#hizmetler .service-overview__item')).not.toHaveCount(0)
    await expect(page.locator('#talep-formu form')).toBeVisible()
    await expect(page.locator('#sss details')).not.toHaveCount(0)
  })
})
