import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { dashboardResponse } from '../helpers/dashboard'
import { ADMIN, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

// Chart.js jsdom'da canvas çizemez; Chart bileşeni aldığı veriyi kaydeden bir taklitle değiştirilir.
const chart = vi.hoisted(() => ({ props: null }))
vi.mock('primevue/chart', async () => {
  const { h } = await import('vue')
  return {
    default: {
      name: 'Chart',
      props: ['type', 'data', 'options'],
      setup(props) {
        return () => {
          chart.props = props
          return h('canvas', { 'data-chart': props.type })
        }
      },
    },
  }
})

let wrapper

afterEach(() => {
  wrapper?.unmount()
  restoreApi()
  window.localStorage.clear()
})

/**
 * Admin oturumu ve verilen dashboard yanıtlayıcısıyla gösterge panelini açar.
 *
 * @param {(config: object) => [number, any]} respond `/admin/dashboard/` yanıtlayıcısı.
 * @returns {Promise<Array<object>>} İstek kaydı.
 */
async function openDashboard(respond) {
  tokenStorage.set({ access: 'a1', refresh: 'r1' })
  const calls = useFakeApi(routeHandler({
    'GET /auth/me/': () => [200, ADMIN],
    'GET /admin/dashboard/': respond,
  }))
  ;({ wrapper } = await mountApp('/admin/dashboard'))
  await vi.waitFor(() => expect(calls.some((call) => call.url === '/admin/dashboard/')).toBe(true), { timeout: 5000 })
  await flushPromises()
  return calls
}

const dashboardCalls = (calls) => calls.filter((call) => call.url === '/admin/dashboard/')
const card = (key) => wrapper.get(`[data-card="${key}"]`)

describe('gösterge paneli kartları', () => {
  it('varsayılan olarak 30 gün ve tüm kaynaklarla yükler', async () => {
    const calls = await openDashboard(() => [200, dashboardResponse()])

    expect(dashboardCalls(calls)[0].params).toEqual({ days: 30, source: 'all' })
  })

  it('dört kartı sırayla, değer ve alt bilgileriyle gösterir', async () => {
    await openDashboard(() => [200, dashboardResponse()])

    expect(wrapper.findAll('.stat-card')).toHaveLength(4)
    expect(card('total-demand').get('.stat-card__value').text()).toBe('1.250')
    expect(card('total-demand').get('.stat-card__trend').classes()).toContain('stat-card__trend--up')
    expect(card('open-requests').get('.stat-card__foot').text()).toBe('3 tanesi henüz incelenmedi')
    expect(card('inquiries').get('.stat-card__trend').classes()).toContain('stat-card__trend--down')
    expect(card('services').get('.stat-card__foot').text()).toBe('En çok talep: Evde bakım')
  })

  it('incelenmemiş başvuru ve talep yoksa buna uygun not gösterir', async () => {
    const response = dashboardResponse()
    response.cards.open_requests.new = 0
    response.cards.services.top_service = null
    await openDashboard(() => [200, response])

    expect(card('open-requests').get('.stat-card__foot').text()).toBe('Hepsi incelendi')
    expect(card('services').get('.stat-card__foot').text()).toBe('Henüz talep gelmedi')
  })

  it('yüklenemezse hata gösterir; tekrar dene ile yeniden ister', async () => {
    let fail = true
    const calls = await openDashboard(() => (fail ? [500, {}] : [200, dashboardResponse()]))

    expect(wrapper.get('[role="alert"]').text()).toContain('Tekrar dene')
    fail = false
    await wrapper.get('[role="alert"] button').trigger('click')
    await flushPromises()

    expect(dashboardCalls(calls)).toHaveLength(2)
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(card('total-demand').get('.stat-card__value').text()).toBe('1.250')
  })

  it('dil değişince hizmet adları için paneli yeniden ister ve İngilizce gösterir', async () => {
    const calls = await openDashboard(() => [200, dashboardResponse()])

    await wrapper.findAll('.preference-controls__flag')[1].trigger('click')
    await flushPromises()

    expect(dashboardCalls(calls)).toHaveLength(2)
    expect(card('total-demand').get('.stat-card__title').text()).toBe('Total demand this month')
    expect(card('total-demand').get('.stat-card__value').text()).toBe('1,250')
  })
})

describe('hizmet trend grafiği', () => {
  /**
   * Grafik başlığındaki seçicide verilen metinli düğmeye basar.
   *
   * @param {string} label Düğme metni.
   */
  async function choose(label) {
    const button = wrapper.get('.trend').findAll('button').find((item) => item.text() === label)
    await button.trigger('click')
    await flushPromises()
  }

  it('her hizmet için bir çizgi çizer', async () => {
    await openDashboard(() => [200, dashboardResponse()])

    expect(wrapper.find('.trend [data-chart="line"]').exists()).toBe(true)
    expect(chart.props.data.datasets.map((dataset) => dataset.label)).toEqual(['Evde bakım', 'Alışveriş desteği'])
  })

  it('aralık ve kaynak seçimi paneli yeni parametrelerle yeniden ister', async () => {
    const calls = await openDashboard(() => [200, dashboardResponse()])

    await choose('90 gün')
    await choose('Başvurular')

    const params = dashboardCalls(calls).map((call) => call.params)
    expect(params).toContainEqual({ days: 90, source: 'all' })
    expect(params.at(-1)).toEqual({ days: 90, source: 'requests' })
  })

  it('haftalık seride ipucu başlığı haftayı belirtir ve tablo sütunu hafta başlangıcıdır', async () => {
    const response = dashboardResponse()
    response.series.bucket = 'week'
    await openDashboard(() => [200, response])

    expect(chart.props.options.plugins.tooltip.callbacks.title([{ label: '6 Eki' }])).toBe('6 Eki haftası')
    expect(wrapper.get('.trend table thead th').text()).toBe('Hafta başlangıcı')
  })

  it('grafiği göremeyenler için aynı veriyi tabloda verir', async () => {
    await openDashboard(() => [200, dashboardResponse()])

    const rows = wrapper.findAll('.trend table tbody tr')
    expect(rows).toHaveLength(3)
    expect(rows[2].text()).toContain('8 Eki')
    expect(rows[2].findAll('td').map((cell) => cell.text())).toEqual(['2', '1'])
  })

  it('seçilen aralıkta hiç kayıt yoksa grafik yerine bilgi gösterir', async () => {
    const response = dashboardResponse()
    response.series.datasets.forEach((dataset) => dataset.counts.fill(0))
    await openDashboard(() => [200, response])

    expect(wrapper.find('.trend [data-chart]').exists()).toBe(false)
    expect(wrapper.get('.trend__empty').text()).toBe('Seçilen aralıkta talep yok.')
  })
})

describe('son gelenler', () => {
  it('kayıtları türleri ve hizmetleriyle listeler, ilgili admin sayfasına bağlar', async () => {
    await openDashboard(() => [200, dashboardResponse()])

    const request = wrapper.get('[data-recent="request-21"]')
    const inquiry = wrapper.get('[data-recent="inquiry-5"]')
    expect(request.text()).toContain('Fatma Demir')
    expect(request.text()).toContain('Başvuru')
    expect(request.attributes('href')).toBe('/admin/requests/21')
    expect(inquiry.text()).toContain('Hızlı talep')
    expect(inquiry.text()).toContain('Alışveriş desteği')
    expect(inquiry.attributes('href')).toBe('/admin/inquiries?id=5')
  })

  it('kayıt yoksa boş durum metni gösterir', async () => {
    await openDashboard(() => [200, dashboardResponse({ recent: [] })])

    expect(wrapper.get('.recent__empty').text()).toBe('Henüz kayıt yok.')
  })
})
