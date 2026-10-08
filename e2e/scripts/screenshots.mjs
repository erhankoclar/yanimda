// scripts/dev/screenshots.sh tarafından e2e konteynerinde çalıştırılır.
// Her yol için 3 genişlikte tam sayfa ekran görüntüsü alır; konsol hatalarını raporlar.
import { chromium } from '@playwright/test'

const BASE = process.env.E2E_BASE_URL || 'http://frontend:5173'
const SESSION = process.env.SHOT_SESSION || 'none'
const PATHS = (process.env.SHOT_PATHS || '/').split(' ').filter(Boolean)
const THEME = process.env.SHOT_THEME === 'dark' ? 'dark' : 'light'
const LOCALE = process.env.SHOT_LOCALE || ''
// Çekimden önce tıklanacak öğe (ör. mobil menü düğmesi); görünmüyorsa atlanır.
const CLICK = process.env.SHOT_CLICK || ''
const SIZES = [[390, 844], [820, 1180], [1366, 900]]
const ADMIN = { email: process.env.E2E_ADMIN_EMAIL || 'admin@yanimda.local', password: process.env.E2E_ADMIN_PASSWORD || 'Yanimda-Admin-2026' }

const browser = await chromium.launch()
const api = await (await browser.newContext({ baseURL: BASE })).request

/**
 * Oturum türüne göre token çifti alır; kurgusal başvuru sahibi gerekirse kaydedilir.
 *
 * @returns {Promise<{ access: string, refresh: string } | null>} Token çifti veya null.
 */
async function tokens() {
  if (SESSION === 'admin') return (await api.post('/api/auth/token/', { data: ADMIN })).json()
  if (SESSION === 'applicant') {
    const email = `shot.${Date.now()}@example.com`
    const password = 'Kurgusal-Parola-2026'
    await api.post('/api/auth/register/', { data: { email, password, first_name: 'Deneme', last_name: 'Kişi' } })
    return (await api.post('/api/auth/token/', { data: { email, password } })).json()
  }
  return null
}

const pair = await tokens()
// Tam sayfa çekim görüntü alanını geçici büyütür; grafikler yeniden çizilirken animasyona yakalanmasın diye
// hareket azaltma tercihi açılır (uygulama bu tercihte grafikleri animasyonsuz çizer).
const context = await browser.newContext({ baseURL: BASE, colorScheme: THEME, reducedMotion: 'reduce' })
await context.addInitScript(([access, refresh, locale]) => {
  if (access) {
    localStorage.setItem('yanimda.access', access)
    localStorage.setItem('yanimda.refresh', refresh)
  }
  if (locale) localStorage.setItem('yanimda.locale', locale)
}, [pair?.access ?? '', pair?.refresh ?? '', LOCALE])
const page = await context.newPage()
page.on('pageerror', (error) => console.log(`CONSOLE pageerror ${error.message}`))
page.on('console', (message) => { if (message.type() === 'error') console.log(`CONSOLE ${message.text()}`) })

for (const path of PATHS) {
  const slug = path.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'root'
  try {
    await page.goto(path, { waitUntil: 'networkidle' })
    for (const [width, height] of SIZES) {
      await page.setViewportSize({ width, height })
      // Grafik gibi boyuta göre yeniden çizilen öğelerin animasyonu bitsin.
      await page.waitForTimeout(900)
      if (CLICK && await page.locator(CLICK).first().isVisible()) {
        await page.locator(CLICK).first().click()
        await page.waitForTimeout(500)
      }
      const file = `/shots/${slug}-${width}.png`
      await page.screenshot({ path: file, fullPage: true })
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      console.log(`SHOT ${path} ${width}px ${file} yatay-tasma=${overflow > 0 ? overflow + 'px' : 'yok'}`)
      // Açılan katman bir sonraki genişliğe taşınmasın diye sayfa yeniden yüklenir.
      if (CLICK) await page.reload({ waitUntil: 'networkidle' })
    }
  } catch (error) {
    console.log(`ERROR ${path} ${error.message}`)
  }
}
await browser.close()
