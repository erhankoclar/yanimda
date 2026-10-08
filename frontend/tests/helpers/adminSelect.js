// PrimeVue Select kök öğesi üzerinden çalışan yardımcılar (erişilebilir adı olmayan seçiciler için).

import { flushPromises } from '@vue/test-utils'
import { expect, vi } from 'vitest'

/**
 * Verilen PrimeVue Select kök öğesini açıp seçeneği seçer.
 *
 * @param {Element} root `.p-select` kök öğesi.
 * @param {string} optionText Seçilecek seçeneğin metni.
 */
export async function chooseFrom(root, optionText) {
  root.dispatchEvent(new MouseEvent('click', { bubbles: true }))
  await flushPromises()
  let option
  await vi.waitFor(() => {
    option = [...document.body.querySelectorAll('[role="option"]')].find((item) => item.textContent.trim() === optionText)
    expect(option).toBeTruthy()
  }, { timeout: 3000 })
  option.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
  await flushPromises()
}

/**
 * Select'i açıp seçenek metinlerini döndürür.
 *
 * @param {Element} root `.p-select` kök öğesi.
 * @returns {Promise<string[]>} Seçenek metinleri.
 */
export async function optionTexts(root) {
  root.dispatchEvent(new MouseEvent('click', { bubbles: true }))
  await flushPromises()
  await vi.waitFor(() => expect(document.body.querySelector('[role="option"]')).toBeTruthy(), { timeout: 3000 })
  return [...document.body.querySelectorAll('[role="option"]')].map((item) => item.textContent.trim())
}
