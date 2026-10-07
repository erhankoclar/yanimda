import { expect, test } from '@playwright/test'

const PAGES = ['/', '/login', '/register']

test.describe('duyarlı düzen', () => {
  for (const path of PAGES) {
    test(`${path} yatay kaydırma oluşturmaz ve konsol hatası vermez`, async ({ page }) => {
      const errors = []
      page.on('pageerror', (error) => errors.push(error.message))
      page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()) })

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
