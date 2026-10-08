import { flushPromises } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { tokenStorage } from '@/api/tokenStorage'

import { dashboardResponse } from '../helpers/dashboard'
import { ADMIN, restoreApi, routeHandler, useFakeApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

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
