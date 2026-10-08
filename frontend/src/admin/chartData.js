import { formatShortDate } from './format'

// Hizmet çizgilerinin renkleri; açık ve koyu zeminde ayırt edilebilecek şekilde seçildi.
export const SERIES_COLORS = ['#2e9c8a', '#f29e4c', '#4a8fd6', '#a46bc0', '#c9a227', '#d9607a', '#6b8f3a', '#8a7a6a']

/**
 * Dashboard `series` yanıtını Chart.js çizgi grafiği verisine çevirir; her hizmet bir çizgidir.
 *
 * @param {{ labels: string[], datasets: Array<{ service_id: number, name: string, counts: number[] }> }} series
 *   Backend'den gelen seri.
 * @returns {{ labels: string[], datasets: Array<object> }} Chart.js `data` nesnesi.
 */
export function toLineChartData(series) {
  return {
    labels: series.labels.map(formatShortDate),
    datasets: series.datasets.map((dataset, index) => {
      const color = SERIES_COLORS[index % SERIES_COLORS.length]
      return {
        label: dataset.name,
        data: dataset.counts,
        borderColor: color,
        backgroundColor: color,
        borderWidth: 2,
        pointRadius: series.labels.length > 31 ? 0 : 3,
        pointHoverRadius: 5,
        // Monoton eğri tam sayılar arasında sıfırın altına veya tepenin üstüne taşmaz.
        cubicInterpolationMode: 'monotone',
      }
    }),
  }
}

/**
 * Serideki tüm sayıların toplamını döndürür; boş grafik durumunu anlamak için kullanılır.
 *
 * @param {{ datasets: Array<{ counts: number[] }> } | null} series Seri.
 * @returns {number} Toplam kayıt sayısı.
 */
export function seriesTotal(series) {
  return (series?.datasets ?? []).reduce((sum, dataset) => sum + dataset.counts.reduce((a, b) => a + b, 0), 0)
}
