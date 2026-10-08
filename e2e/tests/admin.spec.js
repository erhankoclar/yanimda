import { expect, test } from '@playwright/test'

import { ADMIN, uniqueEmail } from './helpers.js'

const PASSWORD = 'Kurgusal-Parola-2026'

// Üretim imajı yerelde düz HTTP üzerinden denenirken tarayıcı, Django'nun gönderdiği
// Cross-Origin-Opener-Policy başlığını yok saydığını bildirir. HTTPS'te (Render) bu uyarı oluşmaz.
const IGNORED_CONSOLE = ['Cross-Origin-Opener-Policy header has been ignored']

/**
 * Sayfadaki konsol hatalarını ve yakalanmamış istisnaları toplar.
 *
 * @param {import('@playwright/test').Page} page Sayfa.
 * @returns {string[]} Dolduğunda hata metinlerini içeren dizi.
 */
function collectErrors(page) {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  page.on('console', (message) => {
    const ignored = IGNORED_CONSOLE.some((text) => message.text().includes(text))
    if (message.type() === 'error' && !ignored) errors.push(message.text())
  })
  return errors
}

/**
 * Yatay kaydırma taşmasını piksel olarak ölçer.
 *
 * @param {import('@playwright/test').Page} page Sayfa.
 * @returns {Promise<number>} Taşma (0 veya negatif ise yok).
 */
function horizontalOverflow(page) {
  return page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
}

/**
 * Yönetici hesabıyla /admin/login üzerinden giriş yapar.
 *
 * @param {import('@playwright/test').Page} page Sayfa.
 */
async function adminLogin(page) {
  await page.goto('/admin/login')
  await page.getByLabel('E-posta adresi').fill(ADMIN.email)
  await page.locator('#admin-password').fill(ADMIN.password)
  await page.getByRole('button', { name: 'Giriş yap' }).click()
  await expect(page).toHaveURL(/\/admin\/dashboard/)
}

/**
 * Projenin (telefon/masaüstü) ayarlarıyla yeni, yalıtılmış bir tarayıcı bağlamı açar.
 *
 * @param {import('@playwright/test').Browser} browser Tarayıcı.
 * @returns {Promise<import('@playwright/test').BrowserContext>} Bağlam.
 */
function newContext(browser) {
  const { baseURL, viewport, userAgent, isMobile, hasTouch, deviceScaleFactor } = test.info().project.use
  return browser.newContext({ baseURL, viewport, userAgent, isMobile, hasTouch, deviceScaleFactor })
}

/**
 * Landing sayfasındaki hızlı talep formunu doldurup gönderir.
 *
 * @param {import('@playwright/test').Page} page Sayfa.
 * @param {{ name: string, email: string, message: string }} data Form verisi.
 */
async function submitQuickInquiry(page, { name, email, message }) {
  await page.goto('/#talep-formu')
  const form = page.locator('#talep-formu')
  await expect(form.getByLabel('Hangi hizmet?').locator('option')).not.toHaveCount(1)
  await form.getByLabel('Adınız ve soyadınız').fill(name)
  await form.getByLabel('E-posta adresiniz').fill(email)
  await form.getByLabel('Hangi hizmet?').selectOption({ index: 1 })
  await form.getByLabel('İlçe', { exact: true }).selectOption({ label: 'Kadıköy' })
  await expect(form.getByLabel('Mahalle', { exact: true })).toBeEnabled()
  await form.getByLabel('Mahalle', { exact: true }).selectOption({ label: 'Caferağa Mahallesi' })
  await form.getByLabel('Kısaca anlatın').fill(message)
  await form.getByRole('checkbox').check()
  await form.getByRole('button', { name: 'Talebimi gönder' }).click()
  await expect(form.getByText('Talebiniz alındı')).toBeVisible()
}

test.describe('yönetici girişi', () => {
  test('/admin/login ile giriş gösterge panelini 4 kart ve grafikle açar', async ({ page }) => {
    const errors = collectErrors(page)

    await adminLogin(page)

    await expect(page.locator('h1')).toHaveText('Gösterge paneli')
    await expect(page.locator('[data-card]')).toHaveCount(4)
    await expect(page.locator('.trend canvas')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Son gelenler' })).toBeVisible()
    expect(await horizontalOverflow(page)).toBeLessThanOrEqual(0)
    expect(errors).toEqual([])
  })

  test('genel /login yöneticiyi gösterge paneline götürür ve başlıkta Yönetim paneli görünür', async ({ page, isMobile }) => {
    await page.goto('/login')
    await page.getByLabel('E-posta adresi').fill(ADMIN.email)
    await page.getByLabel('Parola', { exact: true }).fill(ADMIN.password)
    await page.getByRole('button', { name: 'Giriş yap' }).click()
    await expect(page).toHaveURL(/\/admin\/dashboard/)

    await page.goto('/')
    if (isMobile) await page.locator('.site-header__toggle').click()
    const link = page.getByRole('navigation', { name: 'Hesap' }).getByRole('link', { name: 'Yönetim paneli' })
    await expect(link).toBeVisible()
    await link.click()
    await expect(page).toHaveURL(/\/admin\/dashboard/)
  })

  test('yanlış parola hata gösterir ve panele geçirmez', async ({ page }) => {
    await page.goto('/admin/login')
    await page.getByLabel('E-posta adresi').fill(ADMIN.email)
    await page.locator('#admin-password').fill('Yanlis-Parola-2026')
    await page.getByRole('button', { name: 'Giriş yap' }).click()

    await expect(page.getByRole('alert')).toContainText('E-posta adresi veya parola hatalı.')
    await expect(page).toHaveURL(/\/admin\/login/)
  })
})

test.describe('hızlı talepler', () => {
  test('landing sayfasından bırakılan talep son gelenlerde ve talep listesinde görünür, çekmece mesajı gösterir', async ({ page, browser }) => {
    const unique = Date.now()
    const name = `Deneme Talep ${unique}`
    const message = `Kurgusal test mesajı ${unique}: haftada iki gün refakat.`
    const visitor = await newContext(browser)
    await submitQuickInquiry(await visitor.newPage(), { name, email: uniqueEmail('e2e.admin.talep'), message })
    await visitor.close()

    await adminLogin(page)
    await expect(page.locator('.recent').getByText(name)).toBeVisible()

    await page.goto('/admin/inquiries')
    await page.locator('.admin-list__search input').fill(name)
    const row = page.getByRole('row').filter({ hasText: name })
    await expect(row).toHaveCount(1)
    await row.click()

    const drawer = page.getByRole('dialog')
    await expect(drawer).toContainText(message)
    await expect(drawer).toContainText('Kadıköy')
    await expect(drawer).toContainText('Caferağa')
  })
})

test.describe('başvuru durumu', () => {
  test('yönetici durumu not ile değiştirir, başvuru sahibi yeni durumu görür ama notu görmez', async ({ page, browser }) => {
    const email = uniqueEmail('e2e.admin.basvuru')
    const note = `Yalnızca yönetici görür ${Date.now()}`
    const date = new Date()
    date.setDate(date.getDate() + 3)

    const applicantContext = await newContext(browser)
    const applicant = await applicantContext.newPage()
    await applicant.goto('/register')
    await applicant.getByLabel('Adınız', { exact: true }).fill('Deneme')
    await applicant.getByLabel('Soyadınız', { exact: true }).fill('Başvuran')
    await applicant.getByLabel('E-posta adresi').fill(email)
    await applicant.getByLabel('Parola', { exact: true }).fill(PASSWORD)
    await applicant.getByRole('button', { name: 'Hesabımı oluştur' }).click()
    await expect(applicant.getByRole('heading', { name: 'Hangi konuda desteğe ihtiyacınız var?' })).toBeVisible()
    await applicant.locator('.service-card').first().click()
    await applicant.getByRole('button', { name: 'Devam et' }).click()
    await applicant.getByLabel('Adı ve soyadı').fill('Kurgusal Yaşlı')
    await applicant.getByLabel('Yaşı').fill('80')
    await applicant.getByLabel('Sizin nesiniz?').selectOption('parent')
    await applicant.getByRole('button', { name: 'Devam et' }).click()
    await applicant.getByLabel('Hangi gün?').fill(date.toISOString().slice(0, 10))
    await applicant.getByLabel('Günün hangi saatleri?').selectOption('morning')
    await applicant.getByLabel('İlçe', { exact: true }).selectOption({ label: 'Kadıköy' })
    await expect(applicant.getByLabel('Mahalle', { exact: true })).toBeEnabled()
    await applicant.getByLabel('Mahalle', { exact: true }).selectOption({ label: 'Caferağa Mahallesi' })
    await applicant.getByLabel('Açık adres').fill('Kurgusal Sok. No: 1')
    await applicant.getByRole('button', { name: 'Devam et' }).click()
    await applicant.getByLabel('Size hangi numaradan ulaşalım?').fill('0555 000 00 00')
    await applicant.getByRole('button', { name: 'Devam et' }).click()
    await applicant.getByRole('checkbox').check()
    await applicant.getByRole('button', { name: 'Başvuruyu gönder' }).click()
    await expect(applicant).toHaveURL(/\/requests\/\d+\?created=1/)
    const id = applicant.url().match(/\/requests\/(\d+)/)[1]

    await adminLogin(page)
    await page.goto(`/admin/requests/${id}`)
    // Uygulama hatası: "Yeni durum" etiketi seçim kutusuna bağlanmıyor; soft kontrol akışı durdurmadan başarısız olur.
    await expect.soft(page.getByLabel('Yeni durum'), 'Yeni durum etiketi seçim kutusunu adlandırmalı').toBeVisible({ timeout: 3000 })
    await page.locator('.status-panel').getByRole('combobox').click()
    await page.getByRole('option', { name: 'İnceleniyor' }).click()
    await page.getByLabel('Yönetici notu').fill(note)
    await page.getByRole('button', { name: 'Kaydet' }).click()
    await page.getByRole('button', { name: 'Durumu değiştir' }).click()
    await expect(page.getByText('Değişiklikler kaydedildi.')).toBeVisible()

    await applicant.goto(`/requests/${id}`)
    await expect(applicant.locator('.request-detail__head')).toContainText('İnceleniyor')
    await expect(applicant.locator('body')).not.toContainText(note)
    await applicantContext.close()
  })
})

test.describe('talep haritası', () => {
  test('harita konsol hatası vermeden yüklenir, sıralama listesi ve harita tuvali görünür', async ({ page }) => {
    const errors = collectErrors(page)
    await adminLogin(page)

    await page.goto('/admin/map')

    await expect(page.locator('h1')).toHaveText('Talep haritası')
    await expect(page.getByRole('heading', { name: 'En çok talep gelen yerler' })).toBeVisible()
    await expect(page.getByRole('region', { name: /talep yoğunluğu haritası/ }).locator('canvas')).toBeVisible()
    expect(await horizontalOverflow(page)).toBeLessThanOrEqual(0)
    expect(errors).toEqual([])
  })
})

test.describe('yönetim sayfalarının düzeni', () => {
  for (const path of ['/admin/dashboard', '/admin/inquiries', '/admin/requests', '/admin/users', '/admin/map']) {
    test(`${path} yatay kaydırma oluşturmaz ve konsol hatası vermez`, async ({ page }) => {
      const errors = collectErrors(page)
      await adminLogin(page)

      await page.goto(path)
      await expect(page.locator('h1')).toBeVisible()
      await page.waitForLoadState('networkidle')

      expect(await horizontalOverflow(page)).toBeLessThanOrEqual(0)
      expect(errors).toEqual([])
    })
  }
})
