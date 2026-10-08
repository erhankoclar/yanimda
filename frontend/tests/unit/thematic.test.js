import { describe, expect, it } from 'vitest'

import {
  ISTANBUL_BOUNDS, ZOOM, classBreaks, colorRamp, countFor, fillColorExpression, legendRows, ranked, withCounts,
} from '@/admin/map/thematic'

const LIGHT = colorRamp('light')

describe('colorRamp', () => {
  it('açık ve koyu tema için beş renk döndürür', () => {
    expect(colorRamp('light')).toHaveLength(5)
    expect(colorRamp('dark')).toHaveLength(5)
    expect(colorRamp('dark')).not.toEqual(colorRamp('light'))
  })

  it('bilinmeyen temada açık skalaya düşer', () => {
    expect(colorRamp('sepia')).toEqual(colorRamp('light'))
  })
})

describe('sabitler', () => {
  it('yakınlaştırma eşikleri artan sıradadır', () => {
    expect(ZOOM.min).toBeLessThan(ZOOM.district)
    expect(ZOOM.district).toBeLessThan(ZOOM.neighborhood)
    expect(ZOOM.neighborhood).toBeLessThan(ZOOM.max)
  })

  it('İstanbul sınır kutusu batı-güney-doğu-kuzey sırasındadır', () => {
    const [west, south, east, north] = ISTANBUL_BOUNDS
    expect(west).toBeLessThan(east)
    expect(south).toBeLessThan(north)
  })
})

describe('classBreaks', () => {
  it('veri yoksa boş dizi döndürür', () => {
    expect(classBreaks([])).toEqual([])
  })

  it('yalnızca sıfırlar varsa boş dizi döndürür', () => {
    expect(classBreaks([0, 0, 0])).toEqual([])
  })

  it('tek değerde yalnızca o değeri döndürür', () => {
    expect(classBreaks([5])).toEqual([5])
  })

  it('tekrarlanan değerleri tek sınıfa indirger', () => {
    expect(classBreaks([3, 3, 3, 3, 3, 3])).toEqual([3])
  })

  it('sıfırları yok sayar', () => {
    expect(classBreaks([0, 0, 4])).toEqual([4])
  })

  it('en çok beş sınıfı artan ve benzersiz sınırlarla üretir', () => {
    const breaks = classBreaks([10, 1, 9, 2, 8, 3, 7, 4, 6, 5])

    expect(breaks).toEqual([1, 3, 5, 7, 9])
    expect(breaks).toEqual([...breaks].sort((a, b) => a - b))
    expect(new Set(breaks).size).toBe(breaks.length)
  })

  it('az veride sınıf sayısı azalır ve ilk sınır en küçük sayıdır', () => {
    const breaks = classBreaks([1, 1, 2])

    expect(breaks[0]).toBe(1)
    expect(breaks.length).toBeLessThanOrEqual(5)
    expect(new Set(breaks).size).toBe(breaks.length)
  })

  it('girdi dizisini değiştirmez', () => {
    const values = [3, 1, 2]
    classBreaks(values)
    expect(values).toEqual([3, 1, 2])
  })
})

describe('legendRows', () => {
  it('her sınıf için bir sonraki sınırdan önceki değere kadar aralık üretir', () => {
    const rows = legendRows([1, 3, 5, 7, 9], 10, LIGHT)

    expect(rows.map(({ from, to }) => [from, to])).toEqual([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
  })

  it('beş sınıfta skalanın tüm renklerini sırayla kullanır', () => {
    const rows = legendRows([1, 3, 5, 7, 9], 10, LIGHT)

    expect(rows.map((row) => row.color)).toEqual(LIGHT)
  })

  it('iki sınıfta açık ve koyu uç renkleri kullanır', () => {
    const rows = legendRows([1, 5], 8, LIGHT)

    expect(rows.map((row) => row.color)).toEqual([LIGHT[0], LIGHT[4]])
    expect(rows[1]).toMatchObject({ from: 5, to: 8 })
  })

  it('tek sınıfta orta rengi kullanır', () => {
    expect(legendRows([5], 5, LIGHT)).toEqual([{ from: 5, to: 5, color: LIGHT[2] }])
  })

  it('sınır yoksa boş döndürür', () => {
    expect(legendRows([], 0, LIGHT)).toEqual([])
  })
})

describe('fillColorExpression', () => {
  it('step ifadesini boş renk ve sınır-renk çiftleriyle kurar', () => {
    const expression = fillColorExpression([1, 3], LIGHT, '#eeeeee')

    expect(expression).toEqual([
      'step', ['coalesce', ['get', 'count'], 0], '#eeeeee',
      1, LIGHT[0],
      3, LIGHT[4],
    ])
  })

  it('sınır yoksa yalnızca boş rengi içerir', () => {
    expect(fillColorExpression([], LIGHT, '#eeeeee')).toEqual(['step', ['coalesce', ['get', 'count'], 0], '#eeeeee'])
  })

  it('renkler legendRows ile aynı sırayı izler', () => {
    const breaks = [1, 3, 5, 7, 9]
    const expression = fillColorExpression(breaks, LIGHT, '#fff')
    const colors = expression.slice(3).filter((_, index) => index % 2 === 1)

    expect(colors).toEqual(legendRows(breaks, 10, LIGHT).map((row) => row.color))
  })
})

describe('countFor', () => {
  const item = { count: 7, by_service: { 3: 4, 8: 3 } }

  it('hizmet seçilmediyse toplamı döndürür', () => {
    expect(countFor(item, null)).toBe(7)
  })

  it('hizmet seçiliyse o hizmetin sayısını döndürür', () => {
    expect(countFor(item, 3)).toBe(4)
  })

  it('kaydı olmayan hizmet için sıfır döndürür', () => {
    expect(countFor(item, 99)).toBe(0)
  })

  it('öğe yoksa sıfır döndürür', () => {
    expect(countFor(undefined, null)).toBe(0)
    expect(countFor(null, 3)).toBe(0)
  })
})

describe('withCounts', () => {
  const collection = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', properties: { id: 1005, name: 'Kadıköy' }, geometry: null },
      { type: 'Feature', properties: { id: 1006, name: 'Üsküdar' }, geometry: null },
      { type: 'Feature', properties: { id: 1999, name: 'Bilinmeyen' }, geometry: null },
    ],
  }
  const items = [
    { id: 5, osm_id: 1005, name: 'Kadıköy', count: 7, by_service: { 3: 4, 8: 3 } },
    { id: 6, osm_id: 1006, name: 'Üsküdar', count: 2, by_service: { 8: 2 } },
  ]

  it('osm_id ile eşleyip area_id ve toplam sayıyı ekler', () => {
    const result = withCounts(collection, items, null)

    expect(result.type).toBe('FeatureCollection')
    expect(result.features[0].properties).toMatchObject({ id: 1005, name: 'Kadıköy', area_id: 5, count: 7 })
    expect(result.features[1].properties).toMatchObject({ area_id: 6, count: 2 })
  })

  it('hizmet seçiliyse o hizmetin sayısını yazar', () => {
    const result = withCounts(collection, items, 3)

    expect(result.features.map((feature) => feature.properties.count)).toEqual([4, 0, 0])
  })

  it('eşleşmeyen özelliği sıfır sayı ve boş area_id ile bırakır', () => {
    const result = withCounts(collection, items, null)

    expect(result.features[2].properties).toMatchObject({ id: 1999, area_id: null, count: 0 })
  })

  it('girdi koleksiyonunu değiştirmez', () => {
    withCounts(collection, items, null)

    expect(collection.features[0].properties).toEqual({ id: 1005, name: 'Kadıköy' })
  })
})

describe('ranked', () => {
  const items = [
    { id: 1, name: 'Ümraniye', count: 3, by_service: { 1: 3 } },
    { id: 2, name: 'Şile', count: 3, by_service: { 2: 3 } },
    { id: 3, name: 'Sarıyer', count: 3, by_service: { 1: 1, 2: 2 } },
    { id: 4, name: 'Adalar', count: 9, by_service: { 1: 9 } },
    { id: 5, name: 'Beykoz', count: 0, by_service: {} },
  ]

  it('toplama göre çoktan aza sıralar; eşitlikte Türkçe ad sırasını korur', () => {
    expect(ranked(items, null).map((item) => item.name)).toEqual(['Adalar', 'Sarıyer', 'Şile', 'Ümraniye', 'Beykoz'])
  })

  it('her öğeye value alanı ekler', () => {
    expect(ranked(items, null).map((item) => item.value)).toEqual([9, 3, 3, 3, 0])
  })

  it('hizmet seçiliyse o hizmetin sayısına göre sıralar', () => {
    const result = ranked(items, 2)

    expect(result.map((item) => [item.name, item.value])).toEqual([
      ['Şile', 3], ['Sarıyer', 2], ['Adalar', 0], ['Beykoz', 0], ['Ümraniye', 0],
    ])
  })

  it('girdi dizisini değiştirmez', () => {
    const before = items.map((item) => item.name)
    ranked(items, null)
    expect(items.map((item) => item.name)).toEqual(before)
  })
})
