import { ref, watch } from 'vue'

import { adminApi } from '@/api/admin'
import { i18n } from '@/i18n'
import { parseApiError } from '@/utils/apiErrors'

/**
 * Gösterge paneli verisini yükler; grafik seçimleri veya dil değişince yeniden ister.
 *
 * Hizmet adları sunucuda dile göre çevrildiği için dil değişimi de yeniden yükleme sebebidir.
 * Üst üste gelen isteklerde yalnızca en son isteğin yanıtı kullanılır.
 *
 * @returns {{
 *   days: import('vue').Ref<7 | 30 | 90>,
 *   source: import('vue').Ref<'all' | 'inquiries' | 'requests'>,
 *   data: import('vue').Ref<object | null>,
 *   loading: import('vue').Ref<boolean>,
 *   error: import('vue').Ref<string>,
 *   load: () => Promise<void>,
 * }} Seçimler, yanıt, yüklenme/hata durumu ve yeniden yükleme fonksiyonu.
 */
export function useDashboard() {
  const days = ref(30)
  const source = ref('all')
  const data = ref(null)
  const loading = ref(false)
  const error = ref('')
  let lastRequest = 0

  /** Seçili aralık ve kaynakla paneli yükler. */
  async function load() {
    const requestId = ++lastRequest
    loading.value = true
    error.value = ''
    try {
      const result = await adminApi.dashboard({ days: days.value, source: source.value })
      if (requestId === lastRequest) data.value = result
    } catch (failure) {
      if (requestId === lastRequest) error.value = parseApiError(failure).general
    } finally {
      if (requestId === lastRequest) loading.value = false
    }
  }

  watch([days, source, i18n.global.locale], load)
  load()

  return { days, source, data, loading, error, load }
}
