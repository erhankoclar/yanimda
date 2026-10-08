import { describe, expect, it } from 'vitest'

import { SERIES_COLORS, seriesTotal, toLineChartData } from '@/admin/chartData'

import { dashboardResponse } from '../helpers/dashboard'

describe('hizmet serisi → Chart.js verisi', () => {
  it('her hizmeti ayrı renkte bir çizgiye, tarihleri kısa etikete çevirir', () => {
    const data = toLineChartData(dashboardResponse().series)

    expect(data.labels).toEqual(['6 Eki', '7 Eki', '8 Eki'])
    expect(data.datasets.map((dataset) => dataset.label)).toEqual(['Evde bakım', 'Alışveriş desteği'])
    expect(data.datasets[0].data).toEqual([1, 0, 2])
    expect(data.datasets[0].borderColor).toBe(SERIES_COLORS[0])
    expect(data.datasets[1].borderColor).toBe(SERIES_COLORS[1])
  })

  it('uzun aralıkta noktaları gizler, kısa aralıkta gösterir', () => {
    const short = toLineChartData(dashboardResponse().series)
    const labels = Array.from({ length: 40 }, (_, index) => `2026-08-${String((index % 28) + 1).padStart(2, '0')}`)
    const long = toLineChartData({ labels, datasets: [{ service_id: 1, name: 'Evde bakım', counts: labels.map(() => 1) }] })

    expect(short.datasets[0].pointRadius).toBe(3)
    expect(long.datasets[0].pointRadius).toBe(0)
  })

  it('serideki toplam kayıt sayısını hesaplar; seri yoksa 0 döner', () => {
    expect(seriesTotal(dashboardResponse().series)).toBe(7)
    expect(seriesTotal(null)).toBe(0)
  })
})
