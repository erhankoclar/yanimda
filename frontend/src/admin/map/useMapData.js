import { ref, watch } from 'vue'

import { adminApi } from '@/api/admin'
import { i18n } from '@/i18n'
import { parseApiError } from '@/utils/apiErrors'

const BOUNDARY_FILES = {
  districts: 'istanbul-districts.geojson',
  neighborhoods: 'istanbul-neighborhoods.geojson',
  labels: 'istanbul-labels.geojson',
}

// Sınır dosyaları büyük ve değişmez; uygulama ömrü boyunca bir kez indirilir.
let boundariesRequest = null

/**
 * İlçe, mahalle ve etiket noktası GeoJSON dosyalarını yükler.
 *
 * @returns {Promise<{ districts: object, neighborhoods: object, labels: object }>} Sınır koleksiyonları.
 */
export function loadBoundaries() {
  if (!boundariesRequest) {
    const base = `${import.meta.env.BASE_URL}geo/`
    boundariesRequest = Promise.all(Object.entries(BOUNDARY_FILES).map(async ([key, file]) => {
      const response = await fetch(`${base}${file}`)
      if (!response.ok) throw new Error(`${file}: HTTP ${response.status}`)
      return [key, await response.json()]
    }))
      .then(Object.fromEntries)
      .catch((error) => {
        boundariesRequest = null
        throw error
      })
  }
  return boundariesRequest
}

/**
 * Tematik haritanın verisini yükler; kaynak, dönem veya dil değişince sayıları yeniden ister.
 *
 * Hizmet seçimi istek gerektirmez: yanıt her alan için hizmet bazında sayıları içerir.
 *
 * @returns {{
 *   source: import('vue').Ref<'all' | 'inquiries' | 'requests'>,
 *   days: import('vue').Ref<number | null>,
 *   boundaries: import('vue').Ref<object | null>,
 *   data: import('vue').Ref<object | null>,
 *   loading: import('vue').Ref<boolean>,
 *   error: import('vue').Ref<string>,
 *   load: () => Promise<void>,
 * }} Seçimler, veri ve durum.
 */
export function useMapData() {
  const source = ref('all')
  const days = ref(null)
  const boundaries = ref(null)
  const data = ref(null)
  const loading = ref(false)
  const error = ref('')
  let lastRequest = 0

  /** Sınırları (ilk kez) ve seçili parametrelerle sayıları yükler. */
  async function load() {
    const requestId = ++lastRequest
    loading.value = true
    error.value = ''
    try {
      const params = { source: source.value, ...(days.value ? { days: days.value } : {}) }
      const [geo, counts] = await Promise.all([loadBoundaries(), adminApi.map(params)])
      if (requestId !== lastRequest) return
      boundaries.value = geo
      data.value = counts
    } catch (failure) {
      if (requestId === lastRequest) error.value = parseApiError(failure).general
    } finally {
      if (requestId === lastRequest) loading.value = false
    }
  }

  watch([source, days, i18n.global.locale], load)
  load()

  return { source, days, boundaries, data, loading, error, load }
}

/** Testler arasında sınır önbelleğini temizler. */
export function resetBoundaryCache() {
  boundariesRequest = null
}
