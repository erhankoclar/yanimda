import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { i18n } from '@/i18n'
import { parseApiError } from '@/utils/apiErrors'

export const PAGE_SIZE = 20
const SEARCH_DELAY_MS = 350

/**
 * Sunucu tarafında sayfalanan, sıralanan ve süzülen admin tablolarının durumunu yönetir.
 *
 * Süzgeçler, sayfa ve sıralama URL sorgusunda tutulur: geri tuşu ve paylaşılan bağlantı aynı
 * listeyi açar. Arama yazarken istekler kısa bir gecikmeyle birleştirilir; üst üste gelen
 * isteklerde yalnızca son yanıt kullanılır.
 *
 * @param {(params: Record<string, any>) => Promise<{ count: number, results: Array<object> }>} fetcher Liste isteği.
 * @param {{ filters?: Record<string, any>, ordering?: string }} [options] Süzgeçlerin varsayılan
 *   değerleri (anahtarlar sorgu parametresi adlarıdır) ve varsayılan sıralama (ör. `-created_at`).
 * @returns {{
 *   filters: Record<string, any>, rows: import('vue').Ref<Array<object>>, total: import('vue').Ref<number>,
 *   page: import('vue').Ref<number>, ordering: import('vue').Ref<string>, loading: import('vue').Ref<boolean>,
 *   error: import('vue').Ref<string>, first: import('vue').ComputedRef<number>,
 *   sortField: import('vue').ComputedRef<string | undefined>, sortOrder: import('vue').ComputedRef<number | undefined>,
 *   onPage: (event: { page: number }) => void, onSort: (event: { sortField?: string, sortOrder?: number }) => void,
 *   reset: () => void, load: () => Promise<void>,
 * }} Tablo durumu ve olay işleyicileri.
 */
export function useServerTable(fetcher, { filters: defaults = {}, ordering: defaultOrdering = '' } = {}) {
  const route = useRoute()
  const router = useRouter()

  const filters = reactive({ ...defaults })
  const page = ref(1)
  const ordering = ref(defaultOrdering)
  const rows = ref([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref('')
  let lastRequest = 0
  let searchTimer = null

  /** URL sorgusundaki değerleri durum alanlarına okur. */
  function readQuery() {
    Object.keys(defaults).forEach((key) => {
      const value = route.query[key]
      filters[key] = value === undefined ? defaults[key] : value
    })
    page.value = Math.max(1, Number(route.query.page) || 1)
    ordering.value = route.query.ordering ?? defaultOrdering
  }

  /**
   * Boş olmayan süzgeçlerden istek parametrelerini kurar.
   *
   * @returns {Record<string, any>} Parametreler.
   */
  function params() {
    const result = { page: page.value }
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) result[key] = value
    })
    if (ordering.value) result.ordering = ordering.value
    return result
  }

  /** Geçerli durumu URL'ye yazar; değişmediyse gezinme yapılmaz. */
  function writeQuery() {
    const query = { ...params() }
    if (query.page === 1) delete query.page
    if (query.ordering === defaultOrdering) delete query.ordering
    const current = JSON.stringify(route.query)
    const next = JSON.stringify(Object.fromEntries(Object.entries(query).map(([key, value]) => [key, String(value)])))
    if (current !== next) router.replace({ query })
  }

  /** Listeyi geçerli parametrelerle yükler. */
  async function load() {
    const requestId = ++lastRequest
    loading.value = true
    error.value = ''
    try {
      const result = await fetcher(params())
      if (requestId !== lastRequest) return
      rows.value = result.results
      total.value = result.count
    } catch (failure) {
      if (requestId !== lastRequest) return
      // Silinen bir sayfaya bağlantıyla gelindiyse ilk sayfaya dönülür.
      if (failure?.response?.status === 404 && page.value > 1) {
        page.value = 1
        writeQuery()
        return
      }
      error.value = parseApiError(failure).general
    } finally {
      if (requestId === lastRequest) loading.value = false
    }
  }

  /**
   * DataTable sayfa olayını işler.
   *
   * @param {{ page: number }} event Sıfırdan başlayan sayfa sırası.
   */
  function onPage(event) {
    page.value = event.page + 1
    writeQuery()
  }

  /**
   * DataTable sıralama olayını DRF `ordering` parametresine çevirir.
   *
   * @param {{ sortField?: string, sortOrder?: number }} event Alan ve yön (1 artan, -1 azalan).
   */
  function onSort(event) {
    ordering.value = event.sortField ? `${event.sortOrder === -1 ? '-' : ''}${event.sortField}` : defaultOrdering
    page.value = 1
    writeQuery()
  }

  /** Tüm süzgeçleri varsayılana döndürür. */
  function reset() {
    Object.assign(filters, defaults)
  }

  const first = computed(() => (page.value - 1) * PAGE_SIZE)
  const sortField = computed(() => (ordering.value ? ordering.value.replace(/^-/, '') : undefined))
  const sortOrder = computed(() => (ordering.value ? (ordering.value.startsWith('-') ? -1 : 1) : undefined))

  /**
   * Süzgeçlerin URL'deki değerlerle aynı olup olmadığını söyler; URL'den okunan değişiklik yeniden yazılmaz.
   *
   * @returns {boolean} Aynıysa true.
   */
  function matchesQuery() {
    return Object.keys(defaults).every((key) => String(filters[key] ?? '') === String(route.query[key] ?? defaults[key] ?? ''))
  }

  // Süzgeç değişince ilk sayfaya dönülür; arama metni kısa gecikmeyle uygulanır.
  watch(() => ({ ...filters }), (next, previous) => {
    if (matchesQuery()) return
    const onlySearch = Object.keys(next).every((key) => key === 'search' || next[key] === previous[key])
    clearTimeout(searchTimer)
    const apply = () => {
      page.value = 1
      writeQuery()
    }
    if (onlySearch && 'search' in next) searchTimer = setTimeout(apply, SEARCH_DELAY_MS)
    else apply()
  })

  // URL tek kaynaktır: sorgu değişince durum okunur ve liste yüklenir.
  watch(() => route.query, () => {
    readQuery()
    load()
  }, { immediate: true })

  // Hizmet adları dile göre döndüğü için dil değişince liste yenilenir.
  watch(i18n.global.locale, load)

  return { filters, rows, total, page, ordering, loading, error, first, sortField, sortOrder, onPage, onSort, reset, load }
}
