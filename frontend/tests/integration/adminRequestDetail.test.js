import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest'

import { adminSession, warmAdminViews, callsTo, requestDetail } from '../helpers/adminLists'
import { chooseFrom, optionTexts } from '../helpers/adminSelect'
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

/**
 * Başvuru detayını yanıtlayan yönetici oturumu kurar.
 *
 * @param {object} [detail] Detay yanıtı.
 * @param {Record<string, any>} [routes] Ek yanıtlayıcılar.
 * @returns {Array<object>} İstek kaydı.
 */
function session(detail = requestDetail(), routes = {}) {
  return adminSession({
    'GET /admin/requests/7/': () => [200, detail],
    ...routes,
  })
}

/** Detay sayfasını açıp durum panelinin görünmesini bekler. */
async function openDetail() {
  const mounted = await mountApp('/admin/requests/7')
  wrapper = mounted.wrapper
  await vi.waitFor(() => expect(wrapper.find('.status-panel').exists()).toBe(true), { timeout: 5000 })
  return mounted
}

/**
 * Durum Select'inin kök öğesini döndürür.
 *
 * @returns {Element} `.p-select` öğesi.
 */
function statusSelect() {
  return wrapper.get('.status-panel .p-select').element
}

/**
 * Kaydet düğmesini döndürür.
 *
 * @returns {import('@vue/test-utils').DOMWrapper<HTMLElement>} Düğme.
 */
function saveButton() {
  return wrapper.get('.status-panel button[type="submit"]')
}

/**
 * Onay penceresini gövdeden bulur.
 *
 * @returns {HTMLElement | null} Pencere.
 */
function confirmDialog() {
  return document.body.querySelector('.p-confirmdialog')
}

/** Durum panelindeki formu gönderir. */
async function submitForm() {
  await wrapper.get('.status-panel form').trigger('submit')
  await flushPromises()
}

/**
 * Onay penceresindeki düğmeyi metniyle tıklar.
 *
 * @param {string} label Düğme metni.
 */
async function clickDialogButton(label) {
  const button = [...confirmDialog().querySelectorAll('button')].find((item) => item.textContent.trim() === label)
  button.click()
  await flushPromises()
}

describe('admin başvuru detayı', () => {
  it('bilgi bölümlerini ve başvuru sahibini gösterir', async () => {
    session()
    await openDetail()

    const text = wrapper.text()
    expect(text).toContain('Zaman ve adres')
    expect(text).toContain('Moda Mahallesi, Kadıköy')
    expect(text).toContain('Örnek Mah. No: 1')
    expect(text).toContain('Anne/baba')
    expect(text).toContain('İletişim')
    expect(text).toContain('05551112233')
    expect(text).toContain('Başvuru sahibi')
    expect(wrapper.get('a[href="mailto:ayse@example.com"]').text()).toBe('ayse@example.com')
    expect(wrapper.get('a[href="/admin/users/30"]').text()).toContain('Ayşe Yılmaz')
  })

  it('sadece next_statuses içindeki durumları seçenek olarak sunar', async () => {
    session(requestDetail({ status: 'new', next_statuses: ['reviewing', 'cancelled'] }))
    await openDetail()

    expect(await optionTexts(statusSelect())).toEqual(['İnceleniyor', 'İptal edildi'])
  })

  it('son durumdaki başvuruda seçici yerine ipucu gösterir', async () => {
    session(requestDetail({ status: 'completed', next_statuses: [] }))
    await openDetail()

    expect(wrapper.find('.status-panel .p-select').exists()).toBe(false)
    expect(wrapper.get('.status-panel').text()).toContain('Bu başvuru son durumunda; durumu artık değiştirilemez.')
  })

  it('değişiklik yokken Kaydet düğmesi devre dışıdır, nota yazınca açılır', async () => {
    session()
    await openDetail()
    expect(saveButton().attributes('disabled')).toBeDefined()

    await wrapper.get('#status-note').setValue('Aile ile görüşüldü.')

    expect(saveButton().attributes('disabled')).toBeUndefined()
  })

  it('notu eski haline getirince Kaydet yeniden devre dışı kalır', async () => {
    session(requestDetail({ admin_note: 'Eski not' }))
    await openDetail()

    await wrapper.get('#status-note').setValue('Yeni not')
    await wrapper.get('#status-note').setValue('Eski not')

    expect(saveButton().attributes('disabled')).toBeDefined()
  })

  it('durum değişikliği önce onay ister ve onaylanmadan istek göndermez', async () => {
    const calls = session()
    await openDetail()

    await chooseFrom(statusSelect(), 'İnceleniyor')
    await submitForm()

    await vi.waitFor(() => expect(confirmDialog()).toBeTruthy(), { timeout: 3000 })
    expect(confirmDialog().textContent).toContain('Durum değişsin mi?')
    expect(confirmDialog().textContent).toContain('"Alındı" yerine "İnceleniyor"')
    expect([...confirmDialog().querySelectorAll('button')].map((item) => item.textContent.trim())).toContain('Durumu değiştir')
    expect(callsTo(calls, 'patch', '/admin/requests/7/')).toHaveLength(0)
  })

  it('onaylanınca yalnızca status alanını PATCH eder ve başarı bildirimi gösterir', async () => {
    const calls = session(requestDetail(), {
      'PATCH /admin/requests/7/': (config) => [200, requestDetail({ ...JSON.parse(config.data), next_statuses: ['assigned', 'cancelled'] })],
    })
    await openDetail()

    await chooseFrom(statusSelect(), 'İnceleniyor')
    await submitForm()
    await vi.waitFor(() => expect(confirmDialog()).toBeTruthy(), { timeout: 3000 })
    await clickDialogButton('Durumu değiştir')

    await vi.waitFor(() => expect(callsTo(calls, 'patch', '/admin/requests/7/')).toHaveLength(1), { timeout: 3000 })
    expect(JSON.parse(callsTo(calls, 'patch', '/admin/requests/7/')[0].data)).toEqual({ status: 'reviewing' })
    await vi.waitFor(() => expect(document.body.textContent).toContain('Değişiklikler kaydedildi.'), { timeout: 3000 })
    expect(wrapper.get('.status-panel').text()).toContain('İnceleniyor')
    expect(saveButton().attributes('disabled')).toBeDefined()
  })

  it('Vazgeç denirse istek göndermez', async () => {
    const calls = session()
    await openDetail()

    await chooseFrom(statusSelect(), 'İptal edildi')
    await submitForm()
    await vi.waitFor(() => expect(confirmDialog()).toBeTruthy(), { timeout: 3000 })
    await clickDialogButton('Vazgeç')

    expect(callsTo(calls, 'patch', '/admin/requests/7/')).toHaveLength(0)
    expect(document.body.textContent).not.toContain('Değişiklikler kaydedildi.')
  })

  it('yalnızca not değişince onaysız kaydeder ve yalnızca admin_note gönderir', async () => {
    const calls = session(requestDetail(), {
      'PATCH /admin/requests/7/': (config) => [200, requestDetail(JSON.parse(config.data))],
    })
    await openDetail()

    await wrapper.get('#status-note').setValue('Telefonla ulaşıldı.')
    await submitForm()

    await vi.waitFor(() => expect(callsTo(calls, 'patch', '/admin/requests/7/')).toHaveLength(1), { timeout: 3000 })
    expect(JSON.parse(callsTo(calls, 'patch', '/admin/requests/7/')[0].data)).toEqual({ admin_note: 'Telefonla ulaşıldı.' })
    expect(confirmDialog()?.textContent ?? '').not.toContain('Durum değişsin mi?')
    await vi.waitFor(() => expect(document.body.textContent).toContain('Değişiklikler kaydedildi.'), { timeout: 3000 })
  })

  it('hem durum hem not değişince ikisini birlikte gönderir', async () => {
    const calls = session(requestDetail(), {
      'PATCH /admin/requests/7/': (config) => [200, requestDetail(JSON.parse(config.data))],
    })
    await openDetail()

    await chooseFrom(statusSelect(), 'İptal edildi')
    await wrapper.get('#status-note').setValue('Yakını vazgeçti.')
    await submitForm()
    await vi.waitFor(() => expect(confirmDialog()).toBeTruthy(), { timeout: 3000 })
    await clickDialogButton('Durumu değiştir')

    await vi.waitFor(() => expect(callsTo(calls, 'patch', '/admin/requests/7/')).toHaveLength(1), { timeout: 3000 })
    expect(JSON.parse(callsTo(calls, 'patch', '/admin/requests/7/')[0].data)).toEqual({ status: 'cancelled', admin_note: 'Yakını vazgeçti.' })
  })

  it('400 alan hatalarını ilgili alanın altında gösterir ve başarı bildirimi vermez', async () => {
    session(requestDetail(), {
      'PATCH /admin/requests/7/': () => [400, { admin_note: ['Not en fazla 2000 karakter olabilir.'] }],
    })
    await openDetail()

    await wrapper.get('#status-note').setValue('x')
    await submitForm()

    await vi.waitFor(() => expect(wrapper.find('.status-panel__error').exists()).toBe(true), { timeout: 3000 })
    expect(wrapper.get('.status-panel__error').text()).toBe('Not en fazla 2000 karakter olabilir.')
    expect(document.body.textContent).not.toContain('Değişiklikler kaydedildi.')
    expect(saveButton().attributes('disabled')).toBeUndefined()
  })

  it('durum alanı hatasını durum bölümünde gösterir', async () => {
    session(requestDetail(), {
      'PATCH /admin/requests/7/': () => [400, { status: ['Bu geçiş yapılamaz.'] }],
    })
    await openDetail()

    await chooseFrom(statusSelect(), 'İnceleniyor')
    await submitForm()
    await vi.waitFor(() => expect(confirmDialog()).toBeTruthy(), { timeout: 3000 })
    await clickDialogButton('Durumu değiştir')

    await vi.waitFor(() => expect(wrapper.get('.status-panel').text()).toContain('Bu geçiş yapılamaz.'), { timeout: 3000 })
  })

  it('olmayan başvuruda "Bu başvuru bulunamadı." uyarısı gösterir', async () => {
    adminSession({ 'GET /admin/requests/404/': () => [404, { detail: 'Not found.' }] })
    const mounted = await mountApp('/admin/requests/404')
    wrapper = mounted.wrapper

    await vi.waitFor(() => expect(wrapper.text()).toContain('Bu başvuru bulunamadı.'), { timeout: 5000 })
    expect(wrapper.find('.status-panel').exists()).toBe(false)
  })

  it('sunucu hatasında uyarı ve Tekrar dene düğmesi gösterir', async () => {
    let fail = true
    adminSession({ 'GET /admin/requests/7/': () => (fail ? [500, {}] : [200, requestDetail()]) })
    const mounted = await mountApp('/admin/requests/7')
    wrapper = mounted.wrapper
    await vi.waitFor(() => expect(wrapper.find('[role="alert"]').exists()).toBe(true), { timeout: 5000 })

    fail = false
    await wrapper.get('[role="alert"] button').trigger('click')

    await vi.waitFor(() => expect(wrapper.find('.status-panel').exists()).toBe(true), { timeout: 3000 })
  })

  it('başvurular listesine dönüş bağlantısı vardır', async () => {
    session()
    await openDetail()

    expect(wrapper.find('a[href="/admin/requests"].request-detail__back').exists()).toBe(true)
  })
})
