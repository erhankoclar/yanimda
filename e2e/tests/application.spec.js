import { expect, test } from '@playwright/test'

import { uniqueEmail } from './helpers.js'

const PASSWORD = 'Kurgusal-Parola-2026'

test('hesap açıp 5 adımlı başvuru yapar ve aynı başvuruyu tekrar gönderemez', async ({ page }) => {
  const email = uniqueEmail('e2e.basvuru')
  const date = new Date()
  date.setDate(date.getDate() + 3)
  const isoDate = date.toISOString().slice(0, 10)

  await page.goto('/register')
  await page.getByLabel('Adınız', { exact: true }).fill('Deneme')
  await page.getByLabel('Soyadınız', { exact: true }).fill('Kişi')
  await page.getByLabel('E-posta adresi').fill(email)
  await page.getByLabel('Parola', { exact: true }).fill(PASSWORD)
  await page.getByRole('button', { name: 'Hesabımı oluştur' }).click()
  await expect(page.getByRole('heading', { name: 'Hangi konuda desteğe ihtiyacınız var?' })).toBeVisible()

  /** Sihirbazı aynı yaşlı ve hizmet için doldurur. */
  async function fillWizard(elderName) {
    await page.locator('.service-card').first().click()
    await page.getByRole('button', { name: 'Devam et' }).click()
    await page.getByLabel('Adı ve soyadı').fill(elderName)
    await page.getByLabel('Yaşı').fill('80')
    await page.getByLabel('Sizin nesiniz?').selectOption('parent')
    await page.getByRole('button', { name: 'Devam et' }).click()
    await page.getByLabel('Hangi gün?').fill(isoDate)
    await page.getByLabel('Günün hangi saatleri?').selectOption('morning')
    await page.getByLabel('İlçe', { exact: true }).selectOption({ label: 'Kadıköy' })
    await expect(page.getByLabel('Mahalle', { exact: true })).toBeEnabled()
    await page.getByLabel('Mahalle', { exact: true }).selectOption({ label: 'Caferağa Mahallesi' })
    await page.getByLabel('Açık adres').fill('Kurgusal Mah. Deneme Sok. No: 1')
    await page.getByRole('button', { name: 'Devam et' }).click()
    await page.getByLabel('Size hangi numaradan ulaşalım?').fill('0555 000 00 00')
    await page.getByRole('button', { name: 'Devam et' }).click()
    await page.getByRole('checkbox').check()
    await page.getByRole('button', { name: 'Başvuruyu gönder' }).click()
  }

  await fillWizard('Kurgusal Yaşlı')
  await expect(page.locator('.request-detail__success')).toContainText('Başvurunuz alındı')
  await expect(page).toHaveURL(/\/requests\/\d+\?created=1/)

  await page.goto('/requests/new')
  await fillWizard('KURGUSAL YAŞLI')
  await expect(page.getByText('zaten açık bir başvurunuz var')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Hangi konuda desteğe ihtiyacınız var?' })).toBeVisible()
})
