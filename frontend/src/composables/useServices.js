import { computed, ref } from 'vue'

import { requestsApi } from '@/api/requests'

/**
 * Aktif hizmet listesini yükler ve durumunu (loading/ready/error) yönetir.
 *
 * @returns {{
 *   services: import('vue').Ref<Array<object>>,
 *   status: import('vue').Ref<'idle' | 'loading' | 'ready' | 'error'>,
 *   load: () => Promise<void>,
 *   nameOf: (id: number | null) => string,
 * }} Hizmetler, yükleme durumu, yükleme fonksiyonu ve kimlikten ad bulan yardımcı.
 */
export function useServices() {
  const services = ref([])
  const status = ref('idle')

  /** Hizmetleri sunucudan yükler; hata olursa durum `error` olur. */
  async function load() {
    status.value = 'loading'
    try {
      services.value = await requestsApi.services()
      status.value = 'ready'
    } catch {
      status.value = 'error'
    }
  }

  // Kimlikten hizmet adı eşlemesi; özet ekranında kullanılır.
  const namesById = computed(() => new Map(services.value.map((service) => [service.id, service.name])))

  /**
   * Hizmet kimliğinin adını döndürür.
   *
   * @param {number | null} id Hizmet kimliği.
   * @returns {string} Hizmet adı; bulunamazsa boş metin.
   */
  const nameOf = (id) => namesById.value.get(id) ?? ''

  return { services, status, load, nameOf }
}
