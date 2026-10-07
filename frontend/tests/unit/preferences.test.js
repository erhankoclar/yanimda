import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import { nextTick } from 'vue'

import { http } from '@/api/http'
import { i18n } from '@/i18n'
import { usePreferencesStore } from '@/stores/preferences'

/**
 * Yeni bir Pinia ile tercih deposunu oluşturur.
 *
 * @returns {ReturnType<typeof usePreferencesStore>} Tercih deposu.
 */
function freshStore() {
  setActivePinia(createPinia())
  return usePreferencesStore()
}

describe('tercih deposu', () => {
  it('kayıt yoksa Türkçe ile başlar ve dili belgeye, i18n\'e ve API başlığına uygular', () => {
    const store = freshStore()

    expect(store.locale).toBe('tr')
    expect(i18n.global.locale.value).toBe('tr')
    expect(document.documentElement.lang).toBe('tr')
    expect(http.defaults.headers['Accept-Language']).toBe('tr')
  })

  it('dil değişince her yere uygular ve tercihi saklar', async () => {
    const store = freshStore()

    store.setLocale('en')
    await nextTick()

    expect(i18n.global.locale.value).toBe('en')
    expect(document.documentElement.lang).toBe('en')
    expect(http.defaults.headers['Accept-Language']).toBe('en')
    expect(window.localStorage.getItem('yanimda.locale')).toBe('en')
  })

  it('desteklenmeyen dili yok sayar', () => {
    const store = freshStore()

    store.setLocale('de')

    expect(store.locale).toBe('tr')
    expect(window.localStorage.getItem('yanimda.locale')).toBeNull()
  })

  it('kayıtlı dili ve temayı geri yükler', () => {
    window.localStorage.setItem('yanimda.locale', 'en')
    window.localStorage.setItem('yanimda.theme', 'dark')

    const store = freshStore()

    expect(store.locale).toBe('en')
    expect(store.isDark).toBe(true)
    expect(document.documentElement.dataset.theme).toBe('dark')
  })

  it('bozuk kayıtlı değerlerde varsayılanlara döner', () => {
    window.localStorage.setItem('yanimda.locale', '<script>')
    window.localStorage.setItem('yanimda.theme', 'neon')

    const store = freshStore()

    expect(store.locale).toBe('tr')
    expect(['light', 'dark']).toContain(store.theme)
  })

  it('tema düğmesi açık ve koyu arasında geçer ve tercihi saklar', async () => {
    window.localStorage.setItem('yanimda.theme', 'light')
    const store = freshStore()

    store.toggleTheme()
    await nextTick()
    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(window.localStorage.getItem('yanimda.theme')).toBe('dark')

    store.toggleTheme()
    await nextTick()
    expect(document.documentElement.dataset.theme).toBe('light')
  })
})
