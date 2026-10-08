import { flushPromises, mount } from '@vue/test-utils'
import { AxiosError } from 'axios'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'

import { PAGE_SIZE, useServerTable } from '@/admin/useServerTable'
import { i18n } from '@/i18n'

let wrapper

/**
 * Bir 404 AxiosError'ı üretir.
 *
 * @returns {AxiosError} Sayfa bulunamadı hatası.
 */
function notFound() {
  return new AxiosError('HTTP 404', '404', {}, {}, { status: 404, data: { detail: 'Invalid page.' } })
}

/**
 * Hook'u gerçek bir bellek router'ı içinde bir bileşende çalıştırır.
 *
 * @param {Function} fetcher Liste isteği.
 * @param {object} [options] Hook seçenekleri.
 * @param {string} [path] Başlangıç adresi.
 * @returns {Promise<{ table: ReturnType<typeof useServerTable>, router: import('vue-router').Router }>} Hook çıktısı ve router.
 */
async function mountTable(fetcher, options, path = '/') {
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', component: { render: () => null } }] })
  router.push(path)
  await router.isReady()
  let table
  const Host = defineComponent({
    setup() {
      table = useServerTable(fetcher, options)
      return () => h('div')
    },
  })
  wrapper = mount(Host, { global: { plugins: [router] } })
  await flushPromises()
  return { table, router }
}

/**
 * Boş sayfa yanıtı üreten sahte liste isteği oluşturur.
 *
 * @returns {import('vitest').Mock} Sahte istek.
 */
function okFetcher() {
  return vi.fn(async () => ({ count: 45, results: [{ id: 1 }] }))
}

beforeEach(() => {
  i18n.global.locale.value = 'tr'
})

afterEach(() => {
  wrapper?.unmount()
  vi.useRealTimers()
})

describe('useServerTable', () => {
  it('açılışta listeyi ilk sayfa ve varsayılan süzgeçlerle yükler', async () => {
    const fetcher = okFetcher()

    const { table } = await mountTable(fetcher, { filters: { search: '', status: '' }, ordering: '-created_at' })

    expect(fetcher).toHaveBeenCalledTimes(1)
    expect(fetcher).toHaveBeenCalledWith({ page: 1, ordering: '-created_at' })
    expect(table.rows.value).toEqual([{ id: 1 }])
    expect(table.total.value).toBe(45)
    expect(table.loading.value).toBe(false)
  })

  it('URL sorgusundaki süzgeç, sayfa ve sıralamayı okuyup isteğe taşır', async () => {
    const fetcher = okFetcher()

    const { table } = await mountTable(
      fetcher,
      { filters: { search: '', status: '' }, ordering: '-created_at' },
      '/?search=ayse&status=new&page=3&ordering=status',
    )

    expect(fetcher).toHaveBeenCalledWith({ page: 3, search: 'ayse', status: 'new', ordering: 'status' })
    expect(table.filters.search).toBe('ayse')
    expect(table.page.value).toBe(3)
    expect(table.first.value).toBe(2 * PAGE_SIZE)
  })

  it('geçersiz sayfa numarasını 1 sayar', async () => {
    const fetcher = okFetcher()

    const { table } = await mountTable(fetcher, { filters: { search: '' } }, '/?page=abc')

    expect(table.page.value).toBe(1)
  })

  it('boş süzgeçleri isteğe eklemez', async () => {
    const fetcher = okFetcher()

    await mountTable(fetcher, { filters: { search: '', service: '' } })

    expect(fetcher.mock.calls[0][0]).toEqual({ page: 1 })
  })

  it('onPage sıfırdan başlayan sayfayı 1 tabanlı yapıp URL’ye yazar ve yeniden yükler', async () => {
    const fetcher = okFetcher()
    const { table, router } = await mountTable(fetcher, { filters: { search: '' } })

    table.onPage({ page: 2 })
    await flushPromises()

    expect(router.currentRoute.value.query.page).toBe('3')
    expect(fetcher).toHaveBeenLastCalledWith({ page: 3 })
  })

  it('ilk sayfaya dönünce page parametresini URL’den kaldırır', async () => {
    const fetcher = okFetcher()
    const { table, router } = await mountTable(fetcher, { filters: { search: '' } }, '/?page=2')

    table.onPage({ page: 0 })
    await flushPromises()

    expect(router.currentRoute.value.query.page).toBeUndefined()
  })

  it('onSort alan ve yönü DRF ordering değerine çevirir (azalan için - öneki)', async () => {
    const fetcher = okFetcher()
    const { table, router } = await mountTable(fetcher, { filters: { search: '' }, ordering: '-created_at' })

    table.onSort({ sortField: 'status', sortOrder: 1 })
    await flushPromises()
    expect(fetcher).toHaveBeenLastCalledWith({ page: 1, ordering: 'status' })
    expect(table.sortField.value).toBe('status')
    expect(table.sortOrder.value).toBe(1)

    table.onSort({ sortField: 'status', sortOrder: -1 })
    await flushPromises()
    expect(fetcher).toHaveBeenLastCalledWith({ page: 1, ordering: '-status' })
    expect(table.sortField.value).toBe('status')
    expect(table.sortOrder.value).toBe(-1)
    expect(router.currentRoute.value.query.ordering).toBe('-status')
  })

  it('sıralama kaldırılınca varsayılan sıralamaya döner ve sayfa 1 olur', async () => {
    const fetcher = okFetcher()
    const { table } = await mountTable(fetcher, { filters: { search: '' }, ordering: '-created_at' }, '/?page=2&ordering=status')

    table.onSort({})
    await flushPromises()

    expect(fetcher).toHaveBeenLastCalledWith({ page: 1, ordering: '-created_at' })
  })

  it('sıralama değişince sayfa 1’e döner', async () => {
    const fetcher = okFetcher()
    const { table } = await mountTable(fetcher, { filters: { search: '' } }, '/?page=4')

    table.onSort({ sortField: 'created_at', sortOrder: -1 })
    await flushPromises()

    expect(table.page.value).toBe(1)
  })

  it('sıralama yokken sortField ve sortOrder tanımsızdır', async () => {
    const { table } = await mountTable(okFetcher(), { filters: { search: '' } })

    expect(table.sortField.value).toBeUndefined()
    expect(table.sortOrder.value).toBeUndefined()
  })

  it('seçim süzgeci değişince hemen ve ilk sayfadan yeniden yükler', async () => {
    const fetcher = okFetcher()
    const { table, router } = await mountTable(fetcher, { filters: { search: '', status: '' } }, '/?page=3')

    table.filters.status = 'new'
    await flushPromises()

    expect(fetcher).toHaveBeenLastCalledWith({ page: 1, status: 'new' })
    expect(router.currentRoute.value.query).toEqual({ status: 'new' })
  })

  it('süzgeç temizlenince parametre istekten ve URL’den kalkar', async () => {
    const fetcher = okFetcher()
    const { table, router } = await mountTable(fetcher, { filters: { status: '' } }, '/?status=new')

    table.filters.status = ''
    await flushPromises()

    expect(fetcher).toHaveBeenLastCalledWith({ page: 1 })
    expect(router.currentRoute.value.query.status).toBeUndefined()
  })

  it('reset tüm süzgeçleri varsayılana döndürür', async () => {
    const fetcher = okFetcher()
    const { table } = await mountTable(fetcher, { filters: { status: '', service: '' } }, '/?status=new&service=2')

    table.reset()
    await flushPromises()

    expect(fetcher).toHaveBeenLastCalledWith({ page: 1 })
  })

  it('geri tuşu gibi URL değişimi durumu ve listeyi günceller', async () => {
    const fetcher = okFetcher()
    const { table, router } = await mountTable(fetcher, { filters: { search: '' } })

    await router.push({ query: { search: 'mehmet', page: '2' } })
    await flushPromises()

    expect(table.filters.search).toBe('mehmet')
    expect(table.page.value).toBe(2)
    expect(fetcher).toHaveBeenLastCalledWith({ page: 2, search: 'mehmet' })
  })

  describe('arama gecikmesi', () => {
    beforeEach(() => vi.useFakeTimers())

    it('yazarken 350 ms boyunca istek atmaz, sonra tek istek atar', async () => {
      const fetcher = okFetcher()
      const { table } = await mountTable(fetcher, { filters: { search: '' } })
      expect(fetcher).toHaveBeenCalledTimes(1)

      table.filters.search = 'a'
      await vi.advanceTimersByTimeAsync(200)
      table.filters.search = 'ay'
      await vi.advanceTimersByTimeAsync(200)
      table.filters.search = 'ayş'
      await vi.advanceTimersByTimeAsync(349)
      expect(fetcher).toHaveBeenCalledTimes(1)

      await vi.advanceTimersByTimeAsync(1)
      await flushPromises()

      expect(fetcher).toHaveBeenCalledTimes(2)
      expect(fetcher).toHaveBeenLastCalledWith({ page: 1, search: 'ayş' })
    })

    it('aramada sayfa 1’e döner', async () => {
      const fetcher = okFetcher()
      const { table } = await mountTable(fetcher, { filters: { search: '' } }, '/?page=3')

      table.filters.search = 'x'
      await vi.advanceTimersByTimeAsync(350)
      await flushPromises()

      expect(fetcher).toHaveBeenLastCalledWith({ page: 1, search: 'x' })
    })

    it('arama beklerken seçim süzgeci değişirse beklemeden uygular', async () => {
      const fetcher = okFetcher()
      const { table } = await mountTable(fetcher, { filters: { search: '', status: '' } })

      table.filters.search = 'ay'
      await vi.advanceTimersByTimeAsync(100)
      table.filters.status = 'new'
      await vi.advanceTimersByTimeAsync(0)
      await flushPromises()

      expect(fetcher).toHaveBeenCalledTimes(2)
      expect(fetcher).toHaveBeenLastCalledWith({ page: 1, search: 'ay', status: 'new' })
    })
  })

  it('üst üste isteklerde eski yanıtı yok sayar', async () => {
    const resolvers = []
    const fetcher = vi.fn(() => new Promise((resolve) => resolvers.push(resolve)))
    const { table } = await mountTable(fetcher, { filters: { status: '' } })

    table.filters.status = 'new'
    await flushPromises()
    expect(resolvers).toHaveLength(2)

    // Yeni istek önce biter; eski yanıt sonradan gelir.
    resolvers[1]({ count: 1, results: [{ id: 'yeni' }] })
    await flushPromises()
    resolvers[0]({ count: 9, results: [{ id: 'eski' }] })
    await flushPromises()

    expect(table.rows.value).toEqual([{ id: 'yeni' }])
    expect(table.total.value).toBe(1)
    expect(table.loading.value).toBe(false)
  })

  it('eski isteğin hatası yeni isteğin sonucunu bozmaz', async () => {
    const settlers = []
    const fetcher = vi.fn(() => new Promise((resolve, reject) => settlers.push({ resolve, reject })))
    const { table } = await mountTable(fetcher, { filters: { status: '' } })

    table.filters.status = 'new'
    await flushPromises()
    settlers[1].resolve({ count: 1, results: [{ id: 2 }] })
    await flushPromises()
    settlers[0].reject(new Error('ağ'))
    await flushPromises()

    expect(table.rows.value).toEqual([{ id: 2 }])
    expect(table.error.value).toBe('')
  })

  it('1’den büyük sayfa 404 dönerse ilk sayfaya geri döner', async () => {
    const fetcher = vi.fn(async (params) => {
      if (params.page > 1) throw notFound()
      return { count: 3, results: [{ id: 1 }] }
    })

    const { table, router } = await mountTable(fetcher, { filters: { search: '' } }, '/?page=7')

    expect(table.page.value).toBe(1)
    expect(router.currentRoute.value.query.page).toBeUndefined()
    expect(fetcher).toHaveBeenLastCalledWith({ page: 1 })
    expect(table.rows.value).toEqual([{ id: 1 }])
    expect(table.error.value).toBe('')
  })

  it('ilk sayfadaki 404 hata olarak gösterilir, döngüye girmez', async () => {
    const fetcher = vi.fn(async () => { throw notFound() })

    const { table } = await mountTable(fetcher, { filters: { search: '' } })

    expect(fetcher).toHaveBeenCalledTimes(1)
    expect(table.error.value).not.toBe('')
    expect(table.loading.value).toBe(false)
  })

  it('başka bir hatada hata metnini doldurur ve load ile yeniden denenebilir', async () => {
    const fetcher = vi.fn()
      .mockRejectedValueOnce(new AxiosError('HTTP 500', '500', {}, {}, { status: 500, data: {} }))
      .mockResolvedValueOnce({ count: 1, results: [{ id: 9 }] })

    const { table } = await mountTable(fetcher, { filters: { search: '' } })
    expect(table.error.value).not.toBe('')

    await table.load()

    expect(table.error.value).toBe('')
    expect(table.rows.value).toEqual([{ id: 9 }])
  })

  it('dil değişince listeyi yeniden yükler', async () => {
    const fetcher = okFetcher()
    await mountTable(fetcher, { filters: { search: '' } })
    expect(fetcher).toHaveBeenCalledTimes(1)

    i18n.global.locale.value = 'en'
    await flushPromises()

    expect(fetcher).toHaveBeenCalledTimes(2)
  })
})
