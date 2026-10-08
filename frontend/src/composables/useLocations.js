import { ref } from 'vue'

import { geoApi } from '@/api/geo'

// Konum listeleri değişmediği için uygulama ömrü boyunca bir kez yüklenir ve tüm formlar paylaşır.
const districts = ref([])
const neighborhoodsByDistrict = ref({})
let districtsRequest = null
const neighborhoodRequests = new Map()

/**
 * İlçe ve mahalle listelerini önbellekli yükler; formlar ve özet ekranı aynı listeyi kullanır.
 *
 * @returns {{
 *   districts: import('vue').Ref<Array<{ id: number, name: string }>>,
 *   neighborhoodsByDistrict: import('vue').Ref<Record<number, Array<{ id: number, name: string }>>>,
 *   loadDistricts: () => Promise<void>,
 *   loadNeighborhoods: (districtId: number) => Promise<void>,
 *   districtName: (id: number) => string,
 *   neighborhoodName: (districtId: number, id: number) => string,
 * }} Listeler, yükleyiciler ve ad bulucular.
 */
export function useLocations() {
  /** İlçeleri ilk çağrıda yükler; sonraki çağrılar aynı isteği bekler. */
  function loadDistricts() {
    if (!districtsRequest) {
      districtsRequest = geoApi.districts()
        .then((items) => { districts.value = items })
        .catch((error) => {
          districtsRequest = null
          throw error
        })
    }
    return districtsRequest
  }

  /**
   * Bir ilçenin mahallelerini ilk çağrıda yükler.
   *
   * @param {number} districtId İlçe kimliği.
   */
  function loadNeighborhoods(districtId) {
    if (!districtId) return Promise.resolve()
    if (!neighborhoodRequests.has(districtId)) {
      neighborhoodRequests.set(districtId, geoApi.neighborhoods(districtId)
        .then((items) => { neighborhoodsByDistrict.value = { ...neighborhoodsByDistrict.value, [districtId]: items } })
        .catch((error) => {
          neighborhoodRequests.delete(districtId)
          throw error
        }))
    }
    return neighborhoodRequests.get(districtId)
  }

  /**
   * @param {number} id İlçe kimliği.
   * @returns {string} İlçe adı; yüklenmemişse boş.
   */
  function districtName(id) {
    return districts.value.find((item) => item.id === Number(id))?.name ?? ''
  }

  /**
   * @param {number} districtId İlçe kimliği.
   * @param {number} id Mahalle kimliği.
   * @returns {string} Mahalle adı; yüklenmemişse boş.
   */
  function neighborhoodName(districtId, id) {
    return neighborhoodsByDistrict.value[Number(districtId)]?.find((item) => item.id === Number(id))?.name ?? ''
  }

  return { districts, neighborhoodsByDistrict, loadDistricts, loadNeighborhoods, districtName, neighborhoodName }
}

/** Testler arasında önbelleği temizler. */
export function resetLocationCache() {
  districts.value = []
  neighborhoodsByDistrict.value = {}
  districtsRequest = null
  neighborhoodRequests.clear()
}
