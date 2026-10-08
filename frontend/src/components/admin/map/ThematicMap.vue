<script setup>
import { Map as MapLibreMap, NavigationControl, Popup, setWorkerUrl } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
// MapLibre'nin web worker'ı Vite'ta bağımlılıklarıyla ayrı paket olarak derlenir; adresi kütüphaneye verilir.
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { formatNumber } from '@/admin/format'
import {
  ISTANBUL_BOUNDS, ISTANBUL_CENTER, ZOOM, classBreaks, colorRamp, fillColorExpression, withCounts,
} from '@/admin/map/thematic'

const props = defineProps({
  /** Sınır verisi: `districts`, `neighborhoods` ve `labels` GeoJSON koleksiyonları. */
  boundaries: { type: Object, required: true },
  /** API'deki ilçe sayıları. */
  districts: { type: Array, required: true },
  /** API'deki mahalle sayıları (yalnızca kaydı olanlar). */
  neighborhoods: { type: Array, required: true },
  /** Seçili moddaki il toplamı. */
  total: { type: Number, required: true },
  /** Hizmet kimliği; null ise toplam gösterilir. */
  serviceId: { type: Number, default: null },
  theme: { type: String, default: 'light' },
})

const emit = defineEmits({
  /** Bir alana veya balona tıklandı. */
  select: (area) => ['city', 'district', 'neighborhood'].includes(area?.level),
  /** Yakınlaştırmayla gösterilen seviye değişti. */
  level: (level) => ['city', 'district', 'neighborhood'].includes(level),
})

setWorkerUrl(workerUrl)

const { t } = useI18n()
const container = ref(null)
let map = null
let popup = null

const STYLES = {
  light: 'https://tiles.openfreemap.org/styles/positron',
  dark: 'https://tiles.openfreemap.org/styles/dark',
}
const FONT = ['Noto Sans Bold']
const BOUNDARY_ATTRIBUTION = '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> (ODbL)'

/**
 * Yakınlaştırmaya göre gösterilen seviyeyi döndürür.
 *
 * @param {number} zoom Yakınlaştırma.
 * @returns {'city' | 'district' | 'neighborhood'} Seviye.
 */
function levelAt(zoom) {
  if (zoom < ZOOM.district) return 'city'
  return zoom < ZOOM.neighborhood ? 'district' : 'neighborhood'
}

/**
 * Seçili moddaki sayılarla haritanın kaynak verilerini üretir.
 *
 * @returns {Record<string, object>} Kaynak adından GeoJSON'a eşleme.
 */
function sourceData() {
  const labels = props.boundaries.labels.features
  const pointsOf = (level) => ({ type: 'FeatureCollection', features: labels.filter((feature) => feature.properties.level === level) })
  return {
    districts: withCounts(props.boundaries.districts, props.districts, props.serviceId),
    neighborhoods: withCounts(props.boundaries.neighborhoods, props.neighborhoods, props.serviceId),
    'district-points': withCounts(pointsOf('district'), props.districts, props.serviceId),
    'neighborhood-points': withCounts(pointsOf('neighborhood'), props.neighborhoods, props.serviceId),
    city: {
      type: 'FeatureCollection',
      features: [{ type: 'Feature', geometry: { type: 'Point', coordinates: ISTANBUL_CENTER }, properties: { count: props.total, name: t('admin.map.city') } }],
    },
  }
}

/**
 * Temanın renklerini döndürür; boş alanlar ve çizgiler altlığa göre seçilir.
 *
 * @returns {{ ramp: string[], empty: string, line: string, bubble: string, bubbleText: string, halo: string }} Renkler.
 */
function palette() {
  const dark = props.theme === 'dark'
  return {
    ramp: colorRamp(props.theme),
    empty: dark ? 'rgba(160, 180, 172, 0.06)' : 'rgba(31, 95, 85, 0.04)',
    line: dark ? 'rgba(200, 225, 218, 0.45)' : 'rgba(22, 63, 57, 0.45)',
    bubble: dark ? '#f2a65c' : '#1f5f55',
    bubbleText: dark ? '#1b1206' : '#ffffff',
    halo: dark ? 'rgba(16, 26, 24, 0.85)' : 'rgba(255, 255, 255, 0.9)',
  }
}

/**
 * Bir katmanın sayılarından sınıf aralıklarını hesaplayıp dolgu rengi ifadesini kurar.
 *
 * @param {{ features: Array<{ properties: { count: number } }> }} collection Sayılı koleksiyon.
 * @param {{ ramp: string[], empty: string }} colors Tema renkleri.
 * @returns {Array<any>} MapLibre ifadesi.
 */
function fillColor(collection, colors) {
  return fillColorExpression(classBreaks(collection.features.map((feature) => feature.properties.count)), colors.ramp, colors.empty)
}

// Balon yarıçapı sayının kareköküyle büyür; en büyük alan bile haritayı kapatmaz.
const bubbleRadius = (min, max) => ['interpolate', ['linear'], ['sqrt', ['get', 'count']], 1, min, 40, max]

/** Kaynakları ve katmanları ekler; stil her değiştiğinde yeniden çağrılır. */
function addLayers() {
  const colors = palette()
  const data = sourceData()
  Object.entries(data).forEach(([name, geojson]) => {
    map.addSource(name, { type: 'geojson', data: geojson, attribution: name === 'districts' ? BOUNDARY_ATTRIBUTION : undefined })
  })

  // İl seviyesi: ilçeler tek renkte, İstanbul bir bütün olarak görünür.
  map.addLayer({
    id: 'city-fill', type: 'fill', source: 'districts', maxzoom: ZOOM.district,
    paint: { 'fill-color': props.total ? colors.ramp[2] : colors.empty, 'fill-opacity': 0.35 },
  })
  map.addLayer({
    id: 'district-fill', type: 'fill', source: 'districts', minzoom: ZOOM.district, maxzoom: ZOOM.neighborhood,
    paint: { 'fill-color': fillColor(data.districts, colors), 'fill-opacity': 0.72 },
  })
  map.addLayer({
    id: 'neighborhood-fill', type: 'fill', source: 'neighborhoods', minzoom: ZOOM.neighborhood,
    paint: { 'fill-color': fillColor(data.neighborhoods, colors), 'fill-opacity': 0.72 },
  })
  map.addLayer({
    id: 'neighborhood-line', type: 'line', source: 'neighborhoods', minzoom: ZOOM.neighborhood,
    paint: { 'line-color': colors.line, 'line-width': 0.6 },
  })
  map.addLayer({
    id: 'district-line', type: 'line', source: 'districts',
    paint: { 'line-color': colors.line, 'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.6, 12, 2.2] },
  })

  const bubbles = [
    { id: 'city', source: 'city', maxzoom: ZOOM.district, radius: 34 },
    { id: 'district', source: 'district-points', minzoom: ZOOM.district, maxzoom: ZOOM.neighborhood, radius: bubbleRadius(11, 26) },
    { id: 'neighborhood', source: 'neighborhood-points', minzoom: ZOOM.neighborhood, radius: bubbleRadius(10, 22) },
  ]
  bubbles.forEach(({ id, source, minzoom, maxzoom, radius }) => {
    const zoomRange = { ...(minzoom ? { minzoom } : {}), ...(maxzoom ? { maxzoom } : {}) }
    map.addLayer({
      id: `${id}-bubble`, type: 'circle', source, ...zoomRange, filter: ['>', ['get', 'count'], 0],
      paint: {
        'circle-color': colors.bubble,
        'circle-radius': radius,
        'circle-stroke-color': colors.halo,
        'circle-stroke-width': 2,
        'circle-opacity': 0.92,
      },
    })
    map.addLayer({
      id: `${id}-count`, type: 'symbol', source, ...zoomRange, filter: ['>', ['get', 'count'], 0],
      layout: {
        'text-field': ['to-string', ['get', 'count']],
        'text-font': FONT,
        'text-size': id === 'city' ? 20 : 13,
        'text-allow-overlap': true,
        'text-ignore-placement': true,
      },
      paint: { 'text-color': colors.bubbleText },
    })
  })
}

/** Seçili moddaki sayıları kaynaklara ve renk sınıflarına uygular. */
function refreshData() {
  if (!map?.getSource('districts')) return
  const colors = palette()
  const data = sourceData()
  Object.entries(data).forEach(([name, geojson]) => map.getSource(name).setData(geojson))
  map.setPaintProperty('city-fill', 'fill-color', props.total ? colors.ramp[2] : colors.empty)
  map.setPaintProperty('district-fill', 'fill-color', fillColor(data.districts, colors))
  map.setPaintProperty('neighborhood-fill', 'fill-color', fillColor(data.neighborhoods, colors))
}

/**
 * Tıklanan özelliği seçilen alana çevirir.
 *
 * @param {'city' | 'district' | 'neighborhood'} level Seviye.
 * @param {object} feature MapLibre özelliği.
 */
function selectFeature(level, feature) {
  const { area_id: id, name, count } = feature.properties
  // İl seviyesinde ilçe dolgusuna tıklansa da il toplamı seçilir.
  if (level === 'city') emit('select', { level, id: null, name: t('admin.map.city'), count: props.total })
  else if (id) emit('select', { level, id, name, count })
}

/** Tıklama, imleç ve ipucu olaylarını bağlar. */
function bindEvents() {
  const clickable = [
    ['city', ['city-bubble', 'city-fill']],
    ['district', ['district-bubble', 'district-fill']],
    ['neighborhood', ['neighborhood-bubble', 'neighborhood-fill']],
  ]
  clickable.forEach(([level, layers]) => {
    layers.forEach((layer) => {
      map.on('click', layer, (event) => selectFeature(level, event.features[0]))
      map.on('mouseenter', layer, () => { map.getCanvas().style.cursor = 'pointer' })
      map.on('mouseleave', layer, () => {
        map.getCanvas().style.cursor = ''
        popup?.remove()
      })
    })
    // Alanın üzerinde ad ve sayı ipucu gösterilir.
    map.on('mousemove', layers[1], (event) => {
      const { name, count } = event.features[0].properties
      const text = level === 'city'
        ? `${t('admin.map.city')}: ${formatNumber(props.total)}`
        : `${name}: ${formatNumber(count ?? 0)}`
      popup ??= new Popup({ closeButton: false, closeOnClick: false, className: 'thematic-map__popup' })
      popup.setLngLat(event.lngLat).setText(text).addTo(map)
    })
  })
  map.on('zoomend', () => emit('level', levelAt(map.getZoom())))
}

onMounted(() => {
  map = new MapLibreMap({
    container: container.value,
    style: STYLES[props.theme] ?? STYLES.light,
    bounds: ISTANBUL_BOUNDS,
    fitBoundsOptions: { padding: 16 },
    minZoom: ZOOM.min,
    maxZoom: ZOOM.max,
    maxBounds: [[ISTANBUL_BOUNDS[0] - 1, ISTANBUL_BOUNDS[1] - 0.6], [ISTANBUL_BOUNDS[2] + 1, ISTANBUL_BOUNDS[3] + 0.6]],
    attributionControl: { compact: true },
    dragRotate: false,
    pitchWithRotate: false,
  })
  map.touchZoomRotate.disableRotation()
  map.addControl(new NavigationControl({ showCompass: false }), 'top-right')
  map.on('style.load', addLayers)
  map.once('load', () => {
    bindEvents()
    emit('level', levelAt(map.getZoom()))
  })
})

watch(() => [props.districts, props.neighborhoods, props.serviceId, props.total], refreshData)
// Tema değişince altlık değişir; katmanlar `style.load` ile yeniden eklenir.
watch(() => props.theme, (theme) => map?.setStyle(STYLES[theme] ?? STYLES.light))

onBeforeUnmount(() => {
  popup?.remove()
  map?.remove()
  map = null
})

</script>

<template>
  <div ref="container" class="thematic-map" role="region" :aria-label="t('admin.map.mapLabel')" />
</template>

<style scoped>
.thematic-map {
  width: 100%;
  height: 100%;
  min-height: 24rem;
  border-radius: var(--admin-radius);
  overflow: hidden;
}

:deep(.thematic-map__popup .maplibregl-popup-content) {
  padding: 0.35rem 0.6rem;
  border-radius: 0.5rem;
  background: var(--admin-surface);
  color: var(--admin-ink);
  font-weight: 700;
  box-shadow: var(--admin-shadow);
}

:deep(.thematic-map__popup .maplibregl-popup-tip) {
  display: none;
}
</style>
