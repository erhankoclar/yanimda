// Uçtan uca testlerin ortak yardımcıları. Tüm veriler kurgusaldır.

export const ADMIN = {
  email: process.env.E2E_ADMIN_EMAIL || 'admin@yanimda.local',
  password: process.env.E2E_ADMIN_PASSWORD || 'Yanimda-Admin-2026',
}

/**
 * Her çalıştırmada benzersiz, kurgusal bir e-posta adresi üretir.
 *
 * @param {string} prefix Adresin başı.
 * @returns {string} E-posta adresi.
 */
export function uniqueEmail(prefix) {
  return `${prefix}.${Date.now()}.${Math.floor(Math.random() * 1e6)}@example.com`
}

/**
 * Admin hesabıyla API token'ı alır.
 *
 * @param {import('@playwright/test').APIRequestContext} request Playwright istek bağlamı.
 * @returns {Promise<string>} Access token.
 */
export async function adminToken(request) {
  const response = await request.post('/api/auth/token/', { data: ADMIN })
  if (!response.ok()) throw new Error(`Admin girişi başarısız: ${response.status()}`)
  return (await response.json()).access
}
