import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import BaseCheckbox from '@/components/public/BaseCheckbox.vue'
import BaseInput from '@/components/public/BaseInput.vue'
import BaseSelect from '@/components/public/BaseSelect.vue'
import BaseTextarea from '@/components/public/BaseTextarea.vue'
import PrimaryButton from '@/components/public/PrimaryButton.vue'

describe('BaseInput', () => {
  it('etiketi alana bağlar ve yazılanı v-model ile bildirir', async () => {
    const wrapper = mount(BaseInput, { props: { label: 'Ad', required: true, modelValue: '' } })

    const input = wrapper.get('input')
    expect(wrapper.get('label').attributes('for')).toBe(input.attributes('id'))
    await input.setValue('Ayşe')
    expect(wrapper.emitted('update:modelValue').at(-1)).toEqual(['Ayşe'])
  })

  it('zorunlu olmayan alanı etiketinde belirtir', () => {
    const optional = mount(BaseInput, { props: { label: 'Telefon' } })
    const required = mount(BaseInput, { props: { label: 'Ad', required: true } })

    expect(optional.get('label').text()).toContain('isteğe bağlı')
    expect(required.get('label').text()).not.toContain('isteğe bağlı')
  })

  it('hata ve ipucunu alana aria-describedby ile bağlar', () => {
    const wrapper = mount(BaseInput, { props: { label: 'E-posta', hint: 'Giriş için', error: 'Geçersiz' } })

    const input = wrapper.get('input')
    const describedBy = input.attributes('aria-describedby').split(' ')
    expect(input.attributes('aria-invalid')).toBe('true')
    expect(describedBy).toHaveLength(2)
    describedBy.forEach((id) => expect(wrapper.find(`#${id}`).exists()).toBe(true))
    expect(wrapper.get('[role="alert"]').text()).toBe('Geçersiz')
  })

  it('ek öznitelikleri kapsayıcıya değil input’a aktarır', () => {
    const wrapper = mount(BaseInput, { props: { label: 'Ad' }, attrs: { name: 'first_name', maxlength: '150' } })

    expect(wrapper.get('input').attributes('name')).toBe('first_name')
    expect(wrapper.attributes('name')).toBeUndefined()
  })
})

describe('BaseSelect', () => {
  it('seçenekleri listeler ve seçimi bildirir', async () => {
    const options = [{ value: 'morning', label: 'Sabah' }, { value: 'evening', label: 'Akşam' }]
    const wrapper = mount(BaseSelect, { props: { label: 'Zaman', options, modelValue: '' } })

    expect(wrapper.findAll('option').map((option) => option.text())).toEqual(['Seçin', 'Sabah', 'Akşam'])
    await wrapper.get('select').setValue('evening')
    expect(wrapper.emitted('update:modelValue').at(-1)).toEqual(['evening'])
  })
})

describe('BaseTextarea', () => {
  it('kalan karakter sayısını gösterir', () => {
    const wrapper = mount(BaseTextarea, { props: { label: 'Not', maxlength: 10, modelValue: 'abc' } })

    expect(wrapper.text()).toContain('7 karakter kaldı')
  })
})

describe('BaseCheckbox', () => {
  it('işaretlenince true bildirir', async () => {
    const wrapper = mount(BaseCheckbox, { props: { modelValue: false }, slots: { default: 'Onaylıyorum' } })

    await wrapper.get('input').setValue(true)

    expect(wrapper.emitted('update:modelValue').at(-1)).toEqual([true])
    expect(wrapper.text()).toContain('Onaylıyorum')
  })
})

describe('PrimaryButton', () => {
  it('yüklenirken kilitlenir ve meşgul olarak işaretlenir', () => {
    const wrapper = mount(PrimaryButton, { props: { loading: true }, slots: { default: 'Gönder' } })

    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.attributes('aria-busy')).toBe('true')
  })

  it('varsayılan olarak formu yanlışlıkla göndermeyen button tipindedir', () => {
    expect(mount(PrimaryButton).attributes('type')).toBe('button')
  })
})
