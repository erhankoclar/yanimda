"""İstanbul ilçe ve mahalle sınırlarını OpenStreetMap'ten üretir.

Çıktılar:
- frontend/public/geo/istanbul-districts.geojson      : sadeleştirilmiş ilçe poligonları
- frontend/public/geo/istanbul-neighborhoods.geojson  : sadeleştirilmiş mahalle poligonları
- frontend/public/geo/istanbul-labels.geojson         : ilçe/mahalle etiket noktaları (sayı balonları)
- backend/apps/geo/data/istanbul.json                 : ilçe → mahalle ad listesi (veritabanı varsayılanları)

Kaynak: OpenStreetMap katkıcıları, ODbL 1.0 (https://www.openstreetmap.org/copyright).
Araçlar (yalnızca bu betikte, npx ile): osmtogeojson (MIT), mapshaper (MPL-2.0).

Kullanım: python scripts/geo/build_istanbul_boundaries.py   (Node.js ve npx gerekir)
"""

import json
import pathlib
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
FRONTEND_OUT = ROOT / 'frontend' / 'public' / 'geo'
BACKEND_OUT = ROOT / 'backend' / 'apps' / 'geo' / 'data'

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'
USER_AGENT = 'yanimda-boundary-export/1.0'
ISTANBUL_RELATION = 223474
LEVELS = {'districts': 6, 'neighborhoods': 8}
# Sadeleştirme oranı: tutulacak köşe yüzdesi. Mahalleler küçük olduğu için daha çok köşe tutulur.
SIMPLIFY = {'districts': '8%', 'neighborhoods': '20%'}
OSMTOGEOJSON = 'osmtogeojson@3.0.0-beta.5'
MAPSHAPER = 'mapshaper@0.6.102'


def fetch(level, target):
    """
    Overpass'tan verilen yönetim seviyesindeki sınırları ilişkileri, yolları ve düğümleriyle indirir.

    Args:
        level (int): OSM `admin_level` değeri (6: ilçe, 8: mahalle).
        target (pathlib.Path): Yanıtın yazılacağı dosya.

    Raises:
        RuntimeError: Sunucu beş denemede de JSON döndürmezse.
    """
    query = (
        f'[out:json][timeout:280];rel({ISTANBUL_RELATION});map_to_area->.ist;'
        f'rel(area.ist)["boundary"="administrative"]["admin_level"="{level}"];(._;>;);out body;'
    )
    body = urllib.parse.urlencode({'data': query}).encode()
    for attempt in range(1, 6):
        request = urllib.request.Request(OVERPASS_URL, data=body, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                content = response.read()
            if content.lstrip().startswith(b'{'):
                target.write_bytes(content)
                return
        except OSError as error:
            print(f'  deneme {attempt}: {error}')
        print(f'  deneme {attempt}: sunucu meşgul, 30 sn sonra tekrar')
        time.sleep(30)
    raise RuntimeError(f'Overpass admin_level={level} için yanıt vermedi.')


def npx(*args):
    """
    Bir Node aracını npx ile çalıştırır.

    Args:
        *args (str): Paket adı ve argümanları.

    Raises:
        subprocess.CalledProcessError: Araç hata verirse.
    """
    command = ['npx', '--yes', *args]
    subprocess.run(command, check=True, shell=sys.platform == 'win32')


def slugify(text):
    """
    Türkçe adı küçük harfli, tireli ASCII kimliğe çevirir.

    Args:
        text (str): Ad.

    Returns:
        str: Kimlik (ör. "Küçükçekmece" -> "kucukcekmece").
    """
    text = text.replace('ı', 'i').replace('İ', 'i')
    ascii_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return '-'.join(part for part in ''.join(c if c.isalnum() else ' ' for c in ascii_text).split())


def contains(polygon_rings, point):
    """
    Noktanın bir poligonun içinde olup olmadığını ışın yöntemiyle söyler (delikler hariç tutulur).

    Args:
        polygon_rings (list[list[list[float]]]): Dış halka ve delik halkaları.
        point (list[float]): [boylam, enlem].

    Returns:
        bool: Nokta dış halkanın içinde ve hiçbir deliğin içinde değilse True.
    """
    def inside(ring):
        x, y = point
        result = False
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                result = not result
        return result

    outer, *holes = polygon_rings
    return inside(outer) and not any(inside(hole) for hole in holes)


def polygons_of(geometry):
    """
    Polygon veya MultiPolygon geometrisini poligon listesine çevirir.

    Args:
        geometry (dict): GeoJSON geometrisi.

    Returns:
        list[list[list[list[float]]]]: Poligonlar (her biri halka listesi).
    """
    return [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']


def load(path):
    """
    GeoJSON dosyasını okur.

    Args:
        path (pathlib.Path): Dosya.

    Returns:
        dict: FeatureCollection.
    """
    return json.loads(path.read_text(encoding='utf-8'))


def prepare(kind, work):
    """
    Bir seviyeyi indirir, GeoJSON'a çevirir, sadeleştirir ve etiket noktalarını üretir.

    Args:
        kind (str): `districts` veya `neighborhoods`.
        work (pathlib.Path): Geçici çalışma klasörü.

    Returns:
        tuple[dict, dict]: Sadeleştirilmiş poligonlar ve etiket noktaları (FeatureCollection).
    """
    raw = work / f'{kind}.osm.json'
    full = work / f'{kind}.full.geojson'
    simple = work / f'{kind}.geojson'
    points = work / f'{kind}.points.geojson'
    print(f'[{kind}] OSM verisi indiriliyor')
    fetch(LEVELS[kind], raw)
    print(f'[{kind}] GeoJSON\'a çevriliyor')
    with full.open('w', encoding='utf-8') as handle:
        subprocess.run(['npx', '--yes', OSMTOGEOJSON, str(raw)], check=True, stdout=handle, shell=sys.platform == 'win32')
    # Yalnızca istenen seviyedeki sınır ilişkilerinin poligonları kalır; üye yollar ve düğümler atılır.
    filtered = work / f'{kind}.filtered.geojson'
    source = load(full)
    filtered.write_text(json.dumps({'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'geometry': feature['geometry'],
         'properties': {'id': feature['id'], 'name': feature['properties'].get('name', '')}}
        for feature in source['features']
        if str(feature.get('id', '')).startswith('relation/')
        and feature['properties'].get('admin_level') == str(LEVELS[kind])
        and feature['geometry']['type'] in ('Polygon', 'MultiPolygon')
    ]}, ensure_ascii=False), encoding='utf-8')
    print(f'[{kind}] sadeleştiriliyor')
    npx(MAPSHAPER, str(filtered), '-simplify', SIMPLIFY[kind], 'keep-shapes', '-o', str(simple), 'format=geojson', 'precision=0.00001')
    npx(MAPSHAPER, str(simple), '-points', 'inner', '-o', str(points), 'format=geojson')
    return load(simple), load(points)


def osm_id(feature):
    """
    osmtogeojson kimliğinden (ör. "relation/123") sayısal OSM kimliğini çıkarır.

    Args:
        feature (dict): GeoJSON özelliği.

    Returns:
        int: OSM ilişki kimliği.
    """
    return int(str(feature['properties']['id']).split('/')[-1])


def main():
    """Sınırları üretir ve çıktı dosyalarını yazar."""
    with tempfile.TemporaryDirectory() as folder:
        work = pathlib.Path(folder)
        districts, district_points = prepare('districts', work)
        neighborhoods, neighborhood_points = prepare('neighborhoods', work)

    district_shapes = [(osm_id(feature), polygons_of(feature['geometry'])) for feature in districts['features']]
    names = {osm_id(feature): feature['properties']['name'] for feature in districts['features']}

    def district_of(point):
        """Noktayı içeren ilçenin OSM kimliğini döndürür; yoksa None."""
        for district_id, shapes in district_shapes:
            if any(contains(rings, point) for rings in shapes):
                return district_id
        return None

    neighborhood_district = {}
    for feature in neighborhood_points['features']:
        neighborhood_district[osm_id(feature)] = district_of(feature['geometry']['coordinates'])
    orphans = [osm_id(f) for f in neighborhoods['features'] if neighborhood_district.get(osm_id(f)) is None]

    def clean(collection, extra):
        """Özellikleri yalnızca gerekli alanlarla yeniden yazar."""
        return {'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'geometry': feature['geometry'],
             'properties': {'id': osm_id(feature), 'name': feature['properties']['name'], **extra(feature)}}
            for feature in collection['features'] if osm_id(feature) not in orphans
        ]}

    FRONTEND_OUT.mkdir(parents=True, exist_ok=True)
    BACKEND_OUT.mkdir(parents=True, exist_ok=True)
    attribution = '© OpenStreetMap contributors, ODbL 1.0'
    outputs = {
        'istanbul-districts.geojson': clean(districts, lambda f: {}),
        'istanbul-neighborhoods.geojson': clean(neighborhoods, lambda f: {'district_id': neighborhood_district[osm_id(f)]}),
        'istanbul-labels.geojson': {'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'geometry': feature['geometry'],
             'properties': {'id': osm_id(feature), 'level': level}}
            for level, points in (('district', district_points), ('neighborhood', neighborhood_points))
            for feature in points['features'] if osm_id(feature) not in orphans
        ]},
    }
    for name, data in outputs.items():
        data['attribution'] = attribution
        (FRONTEND_OUT / name).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

    tree = []
    for district_id, district_name in sorted(names.items(), key=lambda item: item[1]):
        tree.append({
            'osm_id': district_id, 'name': district_name, 'slug': slugify(district_name),
            'neighborhoods': sorted(
                ({'osm_id': osm_id(f), 'name': f['properties']['name']}
                 for f in neighborhoods['features'] if neighborhood_district.get(osm_id(f)) == district_id),
                key=lambda item: item['name'],
            ),
        })
    (BACKEND_OUT / 'istanbul.json').write_text(
        json.dumps({'attribution': attribution, 'districts': tree}, ensure_ascii=False, indent=1), encoding='utf-8',
    )
    print(f'ilçe: {len(tree)}, mahalle: {sum(len(d["neighborhoods"]) for d in tree)}, ilçesiz mahalle: {len(orphans)}')


if __name__ == '__main__':
    main()
