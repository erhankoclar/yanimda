import { computed, ref, watch } from 'vue'

import { requestsApi } from '@/api/requests'
import { i18n } from '@/i18n'
import { useLocations } from '@/composables/useLocations'

/**
 * Admin liste süzgeçlerinin hizmet ve ilçe seçeneklerini yükler.
 *
 * Hizmet adları dile göre döndüğü için dil değişince hizmetler yeniden istenir; ilçeler
 * formlarla paylaşılan önbellekten gelir.
 *
 * @returns {{
 *   serviceOptions: import('vue').ComputedRef<Array<{ value: number, label: string }>>,
 *   districtOptions: import('vue').ComputedRef<Array<{ value: number, label: string }>>,
 * }} Seçenekler.
 */
export function useFilterOptions() {
  const services = ref([])
  const { districts, loadDistricts } = useLocations()

  /** Aktif hizmetleri etkin dilde yükler. */
  function loadServices() {
    requestsApi.services().then((items) => { services.value = items }).catch(() => {})
  }

  loadServices()
  loadDistricts().catch(() => {})
  watch(i18n.global.locale, loadServices)

  return {
    serviceOptions: computed(() => services.value.map((service) => ({ value: service.id, label: service.name }))),
    districtOptions: computed(() => districts.value.map((district) => ({ value: district.id, label: district.name }))),
  }
}
