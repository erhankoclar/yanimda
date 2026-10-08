// Tematik haritanın saf hesapları: seviye eşikleri, sınıf aralıkları, renk skalası ve sayıların GeoJSON'a eklenmesi.

/** Yakınlaştırma eşikleri: altında il toplamı, arasında ilçeler, üstünde mahalleler gösterilir. */
export const ZOOM = { min: 7.5, district: 9, neighborhood: 11.5, max: 15 }

/** İstanbul'un sınır kutusu: [batı, güney, doğu, kuzey]. */
export const ISTANBUL_BOUNDS = [27.97, 40.8, 29.95, 41.6]

/** İl toplamının balonu bu noktada gösterilir (Boğaz'ın ortası). */
export const ISTANBUL_CENTER = [29.0, 41.05]

// Tek tonlu yoğunluk skalası (çam yeşili); açık temada açıktan koyuya, koyu temada koyudan parlağa.
const RAMPS = {
  light: ['#e3efeb', '#acd6cd', '#6fb5a6', '#2e7d70', '#163f39'],
  dark: ['#1e3a33', '#2b5a50', '#3f8577', '#6cc3b0', '#b8ece0'],
}

/**
 * Temaya göre beş sınıflı renk skalasını döndürür.
 *
 * @param {'light' | 'dark'} theme Etkin tema.
 * @returns {string[]} Azdan çoğa beş renk.
 */
export function colorRamp(theme) {
  return RAMPS[theme] ?? RAMPS.light
}

/**
 * Sıfırdan büyük değerlerden, yüzdeliklere dayanan en çok beş sınıf alt sınırı üretir.
 *
 * Tekrarlanan sınırlar birleştirilir; böylece az veride daha az sınıf oluşur.
 *
 * @param {number[]} values Alanların sayıları.
 * @returns {number[]} Artan, benzersiz sınıf alt sınırları; ilk değer en küçük sayıdır. Veri yoksa boş.
 */
export function classBreaks(values) {
  const positive = values.filter((value) => value > 0).sort((a, b) => a - b)
  if (!positive.length) return []
  // İlk sınıf en küçük sayıdan başlar; verisi olmayan bir aralık lejantta görünmez.
  const breaks = [positive[0]]
  for (const ratio of [0.2, 0.4, 0.6, 0.8]) {
    const value = positive[Math.min(positive.length - 1, Math.floor(ratio * positive.length))]
    if (value > breaks[breaks.length - 1]) breaks.push(value)
  }
  return breaks
}

/**
 * Sınıf alt sınırlarını lejant satırlarına çevirir.
 *
 * @param {number[]} breaks `classBreaks` çıktısı.
 * @param {number} max En büyük değer.
 * @param {string[]} ramp Renk skalası.
 * @returns {Array<{ from: number, to: number, color: string }>} Lejant satırları.
 */
export function legendRows(breaks, max, ramp) {
  return breaks.map((from, index) => ({
    from,
    to: index + 1 < breaks.length ? breaks[index + 1] - 1 : max,
    color: ramp[rampIndex(index, breaks.length)],
  }))
}

/**
 * Sınıf sırasını renk skalasındaki konuma yayar; az sınıfta açık ve koyu uçlar korunur.
 *
 * @param {number} index Sınıf sırası.
 * @param {number} count Sınıf sayısı.
 * @returns {number} Skaladaki renk sırası (0-4).
 */
function rampIndex(index, count) {
  if (count <= 1) return 2
  return Math.round((index * 4) / (count - 1))
}

/**
 * Sayıya göre dolgu rengi seçen MapLibre `step` ifadesini kurar; sıfır ve verisiz alanlar boş renkte kalır.
 *
 * @param {number[]} breaks Sınıf alt sınırları.
 * @param {string[]} ramp Renk skalası.
 * @param {string} emptyColor Sıfır sayılı alanın rengi.
 * @returns {Array<any>} MapLibre ifadesi.
 */
export function fillColorExpression(breaks, ramp, emptyColor) {
  const expression = ['step', ['coalesce', ['get', 'count'], 0], emptyColor]
  breaks.forEach((value, index) => expression.push(value, ramp[rampIndex(index, breaks.length)]))
  return expression
}

/**
 * Bir alanın seçili moddaki sayısını döndürür.
 *
 * @param {{ count: number, by_service: Record<string, number> }} item Alanın sayıları.
 * @param {number | null} serviceId Hizmet kimliği; null ise toplam.
 * @returns {number} Sayı.
 */
export function countFor(item, serviceId) {
  if (!item) return 0
  return serviceId ? item.by_service[String(serviceId)] ?? 0 : item.count
}

/**
 * Poligon veya nokta koleksiyonunun özelliklerine API'deki sayıları ve adları ekler.
 *
 * Özelliklerin `id` alanı OSM kimliğidir; API öğeleri `osm_id` ile eşlenir.
 *
 * @param {{ features: Array<object> }} collection GeoJSON FeatureCollection.
 * @param {Array<{ osm_id: number, id: number, name: string, count: number, by_service: Record<string, number> }>} items API öğeleri.
 * @param {number | null} serviceId Hizmet kimliği; null ise toplam.
 * @returns {{ type: 'FeatureCollection', features: Array<object> }} Sayılı yeni koleksiyon.
 */
export function withCounts(collection, items, serviceId) {
  const byOsm = new Map(items.map((item) => [item.osm_id, item]))
  return {
    type: 'FeatureCollection',
    features: collection.features.map((feature) => {
      const item = byOsm.get(feature.properties.id)
      return {
        ...feature,
        properties: {
          ...feature.properties,
          area_id: item?.id ?? null,
          count: countFor(item, serviceId),
        },
      }
    }),
  }
}

/**
 * Alanları seçili moddaki sayıya göre sıralar; eşitlikte ad sırası korunur.
 *
 * @param {Array<{ name: string, count: number, by_service: Record<string, number> }>} items Alanlar.
 * @param {number | null} serviceId Hizmet kimliği; null ise toplam.
 * @returns {Array<object>} `value` alanı eklenmiş, çoktan aza sıralı alanlar.
 */
export function ranked(items, serviceId) {
  return items
    .map((item) => ({ ...item, value: countFor(item, serviceId) }))
    .sort((a, b) => b.value - a.value || a.name.localeCompare(b.name, 'tr'))
}
