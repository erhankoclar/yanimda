import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    // Compose ağındaki tarayıcı testleri siteye servis adıyla erişir.
    allowedHosts: ['frontend'],
    // Windows'tan Docker'a bağlanan klasörlerde dosya olayları iletilmediği için yoklama kullanılır.
    watch: process.env.VITE_USE_POLLING === 'true' ? { usePolling: true, interval: 300 } : undefined,
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    include: ['tests/{unit,component,integration,security,regression,accessibility}/**/*.test.js'],
    restoreMocks: true,
    setupFiles: ['tests/setup.js'],
    // jsdom'daki axe taramaları ve soğuk önbellekte bir dosyanın ilk testi (tembel parçaların ilk
    // derlenmesi) yük altında uzun sürebiliyor.
    testTimeout: 30000,
    // Paket büyüdükçe tam paralel çalışmada tembel admin parçalarının ilk derlenmesi zaman aşımına
    // düşebiliyordu; eş zamanlı test dosyası sayısı sınırlanarak sonuç kararlı tutulur.
    maxWorkers: 3,
  },
})
