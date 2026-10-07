import { describe, expect, it } from 'vitest'

import en from '@/i18n/locales/en'
import tr from '@/i18n/locales/tr'

/**
 * İç içe bir çeviri nesnesindeki tüm yaprak anahtarlarını nokta yoluyla listeler.
 *
 * @param {Record<string, any>} node Çeviri nesnesi.
 * @param {string} [prefix] Üst anahtar yolu.
 * @returns {Array<[string, any]>} [yol, değer] çiftleri.
 */
function leaves(node, prefix = '') {
  return Object.entries(node).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key
    return value && typeof value === 'object' ? leaves(value, path) : [[path, value]]
  })
}

describe('çeviri kataloğu', () => {
  it('Türkçe ve İngilizce katalog tam olarak aynı anahtarlara sahiptir', () => {
    const turkish = leaves(tr).map(([path]) => path).sort()
    const english = leaves(en).map(([path]) => path).sort()

    expect(english).toEqual(turkish)
  })

  it('hiçbir çeviri boş metin ya da metin dışı bir değer değildir', () => {
    for (const [name, catalog] of [['tr', tr], ['en', en]]) {
      for (const [path, value] of leaves(catalog)) {
        expect(typeof value, `${name}:${path}`).toBe('string')
        expect(value.trim(), `${name}:${path}`).not.toBe('')
      }
    }
  })

  it('yer tutucular iki dilde de aynıdır', () => {
    const placeholders = (text) => [...text.matchAll(/\{(\w+)\}/g)].map((match) => match[1]).sort()
    const english = Object.fromEntries(leaves(en))

    for (const [path, value] of leaves(tr)) {
      expect(placeholders(english[path]), path).toEqual(placeholders(value))
    }
  })
})
