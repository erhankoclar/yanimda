import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'

import { adminSession, warmAdminViews, inquiryItem, paged, requestDetail, requestListItem, userItem, waitForRows } from '../helpers/adminLists'
import { chooseFrom } from '../helpers/adminSelect'
import { axeViolations } from '../helpers/axe'
import { restoreApi } from '../helpers/fakeApi'
import { mountApp } from '../helpers/mountApp'

let wrapper

beforeAll(warmAdminViews, 90000)

afterEach(() => {
  wrapper?.unmount()
  document.body.innerHTML = ''
  restoreApi()
  window.localStorage.clear()
})

/** Tüm admin liste ve detay uç noktalarını yanıtlayan oturum kurar. */
function session() {
  return adminSession({
    'GET /admin/inquiries/': () => [200, paged([inquiryItem(1), inquiryItem(2, { location: null })], 45)],
    'GET /admin/inquiries/7/': () => [200, inquiryItem(7)],
    'GET /admin/requests/': () => [200, paged([requestListItem(5), requestListItem(6, { status: 'reviewing' })], 45)],
    'GET /admin/requests/7/': () => [200, requestDetail()],
    'GET /admin/users/': () => [200, paged([userItem(12), userItem(13, { is_staff: true, is_active: false, last_login: null })], 45)],
    'GET /admin/users/12/': () => [200, userItem(12)],
  })
}

describe('admin liste ve detay ekranlarının erişilebilirliği', () => {
  it('hızlı talepler listesi axe ihlali içermez', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/inquiries'))
    await waitForRows(wrapper, 2)

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('başvurular listesi axe ihlali içermez', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/requests'))
    await waitForRows(wrapper, 2)

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('kullanıcılar listesi axe ihlali içermez', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/users'))
    await waitForRows(wrapper, 2)

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('başvuru detayı axe ihlali içermez', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/requests/7'))
    await vi.waitFor(() => expect(wrapper.find('.status-panel').exists()).toBe(true), { timeout: 5000 })

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('kullanıcı detayı axe ihlali içermez', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/users/12'))
    await vi.waitFor(() => expect(wrapper.find('#user-name').exists()).toBe(true), { timeout: 5000 })
    await waitForRows(wrapper, 2)

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('durum paneli hata gösterirken axe ihlali içermez', async () => {
    adminSession({
      'GET /admin/requests/7/': () => [200, requestDetail()],
      'PATCH /admin/requests/7/': () => [400, { admin_note: ['Not çok uzun.'] }],
    })
    ;({ wrapper } = await mountApp('/admin/requests/7'))
    await vi.waitFor(() => expect(wrapper.find('.status-panel').exists()).toBe(true), { timeout: 5000 })
    await wrapper.get('#status-note').setValue('x')
    await wrapper.get('.status-panel form').trigger('submit')
    await vi.waitFor(() => expect(wrapper.find('.status-panel__error').exists()).toBe(true), { timeout: 3000 })

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('açık hızlı talep çekmecesi axe ihlali içermez', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/inquiries?id=7'))
    await vi.waitFor(() => expect(document.body.querySelector('.inquiry-drawer')).toBeTruthy(), { timeout: 5000 })
    await flushPromises()

    expect(await axeViolations(document.body.querySelector('.inquiry-drawer'))).toEqual([])
  })

  it('durum onay penceresi axe ihlali içermez', async () => {
    session()
    ;({ wrapper } = await mountApp('/admin/requests/7'))
    await vi.waitFor(() => expect(wrapper.find('.status-panel').exists()).toBe(true), { timeout: 5000 })
    await chooseFrom(wrapper.get('.status-panel .p-select').element, 'İnceleniyor')
    await wrapper.get('.status-panel form').trigger('submit')
    await vi.waitFor(() => expect(document.body.querySelector('.p-confirmdialog')).toBeTruthy(), { timeout: 3000 })
    await flushPromises()

    expect(await axeViolations(document.body.querySelector('.p-confirmdialog'))).toEqual([])
  })
})
