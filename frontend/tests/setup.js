import { config } from '@vue/test-utils'
import { afterEach, beforeEach } from 'vitest'

import { resetLocationCache } from '@/composables/useLocations'
import { DEFAULT_LOCALE, i18n } from '@/i18n'

import { restoreApi } from './helpers/fakeApi'

// Tek başına bağlanan bileşenler de çeviri kullanabilsin diye i18n her mount'a eklenir.
config.global.plugins = [i18n]

// Her test varsayılan sahte API ve Türkçe ile başlar, temiz bir localStorage ile biter.
beforeEach(() => {
  restoreApi()
  resetLocationCache()
  i18n.global.locale.value = DEFAULT_LOCALE
  delete document.documentElement.dataset.theme
})
afterEach(() => window.localStorage.clear())
