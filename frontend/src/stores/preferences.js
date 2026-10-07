import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

import { http } from '@/api/http'
import { DEFAULT_LOCALE, SUPPORTED_LOCALES, i18n } from '@/i18n'

const LOCALE_KEY = 'yanimda.locale'
const THEME_KEY = 'yanimda.theme'

/**
 * localStorage'dan güvenli şekilde okur.
 *
 * @param {string} key Anahtar.
 * @returns {string | null} Değer; depolama erişilemezse null.
 */
function read(key) {
  try {
    return window.localStorage.getItem(key)
  } catch {
    return null
  }
}

/**
 * localStorage'a güvenli şekilde yazar.
 *
 * @param {string} key Anahtar.
 * @param {string} value Değer.
 */
function write(key, value) {
  try {
    window.localStorage.setItem(key, value)
  } catch {
    // Depolama yoksa seçim yalnızca sayfa açıkken geçerli olur.
  }
}

/**
 * Kullanıcı bir tema seçmediyse cihazın renk şeması tercihini döndürür.
 *
 * @returns {'light' | 'dark'} Cihaz teması.
 */
function systemTheme() {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export const usePreferencesStore = defineStore('preferences', () => {
  const savedLocale = read(LOCALE_KEY)
  const savedTheme = read(THEME_KEY)
  const locale = ref(SUPPORTED_LOCALES.includes(savedLocale) ? savedLocale : DEFAULT_LOCALE)
  const theme = ref(savedTheme === 'dark' || savedTheme === 'light' ? savedTheme : systemTheme())

  // Koyu tema açık mı; tema düğmesinin simgesi ve etiketi buna göre seçilir.
  const isDark = computed(() => theme.value === 'dark')

  /**
   * Dili uygular: i18n, `<html lang>` ve API'ye giden Accept-Language başlığı.
   *
   * @param {string} value Dil kodu.
   */
  function applyLocale(value) {
    i18n.global.locale.value = value
    document.documentElement.lang = value
    http.defaults.headers['Accept-Language'] = value
  }

  /**
   * Temayı `<html data-theme>` özniteliğiyle uygular; renkler CSS değişkenlerinden gelir.
   *
   * @param {string} value `light` veya `dark`.
   */
  function applyTheme(value) {
    document.documentElement.dataset.theme = value
    document.documentElement.style.colorScheme = value
  }

  /**
   * Dili değiştirir ve tercihi saklar.
   *
   * @param {string} value `tr` veya `en`.
   */
  function setLocale(value) {
    if (!SUPPORTED_LOCALES.includes(value)) return
    locale.value = value
    write(LOCALE_KEY, value)
  }

  /** Açık ve koyu tema arasında geçiş yapar ve tercihi saklar. */
  function toggleTheme() {
    theme.value = isDark.value ? 'light' : 'dark'
    write(THEME_KEY, theme.value)
  }

  watch(locale, applyLocale, { immediate: true })
  watch(theme, applyTheme, { immediate: true })

  return { locale, theme, isDark, setLocale, toggleTheme }
})
