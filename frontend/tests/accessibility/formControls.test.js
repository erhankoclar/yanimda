import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'
import { h } from 'vue'

import BaseCheckbox from '@/components/public/BaseCheckbox.vue'
import BaseInput from '@/components/public/BaseInput.vue'
import BaseSelect from '@/components/public/BaseSelect.vue'
import BaseTextarea from '@/components/public/BaseTextarea.vue'
import PrimaryButton from '@/components/public/PrimaryButton.vue'

import { axeViolations } from '../helpers/axe'

let wrapper

afterEach(() => wrapper?.unmount())

describe('form bileşenleri erişilebilirliği', () => {
  it('hatalı ve ipuçlu alanlarla dolu bir form axe ihlali içermez', async () => {
    wrapper = mount({
      render: () => h('form', [
        h(BaseInput, { label: 'Ad', required: true, error: 'Adınızı yazın' }),
        h(BaseInput, { label: 'Telefon', hint: '05xx xxx xx xx', type: 'tel' }),
        h(BaseSelect, { label: 'Zaman', options: [{ value: 'a', label: 'Sabah' }] }),
        h(BaseTextarea, { label: 'Not', maxlength: 100 }),
        h(BaseCheckbox, { required: true }, () => 'Onaylıyorum'),
        h(PrimaryButton, { type: 'submit' }, () => 'Gönder'),
      ]),
    }, { attachTo: document.body })

    expect(await axeViolations(wrapper.element)).toEqual([])
  })

  it('aynı bileşenden birden fazlası benzersiz kimlik kullanır', () => {
    wrapper = mount({
      render: () => h('div', [h(BaseInput, { label: 'A' }), h(BaseInput, { label: 'B' })]),
    })

    const ids = wrapper.findAll('input').map((input) => input.attributes('id'))
    expect(new Set(ids).size).toBe(2)
  })
})
