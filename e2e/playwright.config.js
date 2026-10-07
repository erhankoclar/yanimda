import { defineConfig, devices } from '@playwright/test'

// Testler çalışan yığına (docker compose) karşı koşar; gerçek backend ve PostgreSQL kullanılır.
export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'telefon', use: { ...devices['Pixel 7'] } },
    { name: 'masaustu', use: { viewport: { width: 1366, height: 900 } } },
  ],
})
