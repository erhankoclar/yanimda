import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { useRequestWizardStore } from '@/stores/requestWizard'
import { isoDateAfter } from '@/utils/dates'

import { routeHandler, useFakeApi } from '../helpers/fakeApi'

const DRAFT_KEY = 'yanimda.requestDraft'

/**
 * Store'u tüm adımları geçerli verilerle doldurulmuş hale getirir.
 *
 * @param {ReturnType<typeof useRequestWizardStore>} wizard Sihirbaz store'u.
 */
function fillAll(wizard) {
  Object.assign(wizard.form, {
    service: 7,
    elder_full_name: 'Fatma Yılmaz',
    elder_age: '78',
    relationship: 'parent',
    preferred_date: isoDateAfter(3),
    time_slot: 'morning',
    city: 'Samsun',
    district: 'İlkadım',
    address: 'Örnek Mah. No: 1',
    contact_phone: '0555 111 22 33',
    consent: true,
  })
  wizard.step = 4
}

beforeEach(() => {
  window.sessionStorage.clear()
  setActivePinia(createPinia())
})

describe('başvuru sihirbazı store', () => {
  it('geçersiz adımda ilerlemez ve hataları yazar', () => {
    const wizard = useRequestWizardStore()

    expect(wizard.next()).toBe(false)

    expect(wizard.step).toBe(0)
    expect(wizard.errors).toHaveProperty('service')
  })

  it('bağlantıdan gelen hizmeti ve profildeki telefonu ön doldurur', () => {
    const wizard = useRequestWizardStore()

    wizard.start({ serviceId: 4, phone: '05551112233' })

    expect(wizard.form.service).toBe(4)
    expect(wizard.form.contact_phone).toBe('05551112233')
  })

  it('taslağı oturum deposuna yazar ve yeni store’da geri yükler', () => {
    const first = useRequestWizardStore()
    first.form.service = 4
    first.next()
    first.form.elder_full_name = 'Fatma'

    setActivePinia(createPinia())
    const restored = useRequestWizardStore()
    restored.start()

    expect(restored.step).toBe(1)
    expect(restored.form.elder_full_name).toBe('Fatma')
  })

  it('özetten yalnızca önceki adımlara dönülebilir', () => {
    const wizard = useRequestWizardStore()
    fillAll(wizard)

    wizard.goTo(2)
    expect(wizard.step).toBe(2)
    wizard.goTo(4)
    expect(wizard.step).toBe(2)
  })

  it('başarılı gönderimde doğru veriyi yollar, formu ve taslağı temizler', async () => {
    const calls = useFakeApi(routeHandler({ 'POST /requests/': () => [201, { id: 15 }] }))
    const wizard = useRequestWizardStore()
    fillAll(wizard)

    const created = await wizard.submit()

    expect(created).toEqual({ id: 15 })
    const payload = JSON.parse(calls[0].data)
    expect(payload).toMatchObject({ service: 7, elder_age: 78, consent: true, city: 'Samsun' })
    expect(wizard.step).toBe(0)
    expect(wizard.form.elder_full_name).toBe('')
    expect(window.sessionStorage.getItem(DRAFT_KEY)).toBeNull()
  })

  it('sunucu mükerrer başvuru hatasında hizmet adımına döner ve mesajı gösterir', async () => {
    useFakeApi(routeHandler({
      'POST /requests/': () => [400, { service: ['Fatma Yılmaz için bu hizmette zaten açık bir başvurunuz var.'] }],
    }))
    const wizard = useRequestWizardStore()
    fillAll(wizard)

    const created = await wizard.submit()

    expect(created).toBeNull()
    expect(wizard.step).toBe(0)
    expect(wizard.errors.service).toContain('zaten açık bir başvurunuz var')
    expect(wizard.form.elder_full_name).toBe('Fatma Yılmaz')
  })

  it('ağ hatasında verileri korur ve genel mesaj gösterir', async () => {
    useFakeApi(routeHandler({}))
    const wizard = useRequestWizardStore()
    fillAll(wizard)
    useFakeApi(() => { throw new Error('ağ yok') })

    const created = await wizard.submit()

    expect(created).toBeNull()
    expect(wizard.step).toBe(4)
    expect(wizard.generalError).toContain('Sunucuya ulaşılamadı')
  })
})
