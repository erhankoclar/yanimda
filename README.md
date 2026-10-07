# Yanımda

[English](README.en.md)

Yanımda, yaşlı yakını için evde bakım, refakat, hastane eşliği gibi hizmetlere başvuru yapan aileler ile bu başvuruları yöneten ekip için geliştirilen bir web uygulamasıdır.

- **Son kullanıcı arayüzü:** sade, sıcak, mobil öncelikli; başvuru adım adım (sihirbaz) ilerler.
- **Admin paneli:** talepleri, kullanıcıları ve istatistikleri yöneten yoğun bilgi ekranları (PrimeVue).
- **API:** Django REST Framework, PostgreSQL, JWT kimlik doğrulama.

> **Durum:** Backend API'nin tamamı, son kullanıcı arayüzü (ana sayfa, giriş, kayıt, 5 adımlı başvuru sihirbazı, başvurularım ve başvuru detayı) ve tek tıkla çalıştırma hazırdır. Admin panel ekranları yapım aşamasındadır.

## İçindekiler

- [Hızlı başlangıç](#hızlı-başlangıç)
- [Adresler ve giriş bilgileri](#adresler-ve-giriş-bilgileri)
- [Durdurma ve sıfırlama](#durdurma-ve-sıfırlama)
- [Mimari](#mimari)
- [İş kuralları](#iş-kuralları)
- [API](#api)
- [Ayarlar](#ayarlar)
- [Testler](#testler)
- [Betikler olmadan geliştirme](#betikler-olmadan-geliştirme)
- [Güvenlik notları](#güvenlik-notları)
- [Git akışı](#git-akışı)
- [Sorun giderme](#sorun-giderme)

## Hızlı başlangıç

Tek yapmanız gereken işletim sisteminize uygun dosyayı çalıştırmak. Betik:

1. Docker yoksa kurar,
2. Docker'ı başlatır ve hazır olmasını bekler,
3. Veritabanı, backend ve frontend'i **sırayla** ayağa kaldırır,
4. Siteyi tarayıcınızda açar.

| İşletim sistemi | Başlatma | Durdurma |
| --- | --- | --- |
| Windows 10/11 | `start-windows.bat` dosyasına çift tıklayın | `stop-windows.bat` |
| macOS | `start-mac.command` dosyasına çift tıklayın | `stop-mac.command` |
| Linux | Terminalde `./start-linux.sh` | `./stop-linux.sh` |

Tarayıcı açılmasın istiyorsanız: Windows'ta `start-windows.bat -NoBrowser`, macOS/Linux'ta `--no-browser`.

### Docker kurulumu nasıl yapılır?

| Sistem | Yöntem | Dikkat edilecekler |
| --- | --- | --- |
| Windows | `winget install Docker.DockerDesktop`; winget yoksa resmi kurulum dosyası indirilir ve sessiz kurulur | Yönetici onayı istenir. İlk kurulumdan sonra WSL 2 için **bilgisayarı yeniden başlatmanız** gerekebilir; ardından betiği tekrar çalıştırın. |
| macOS | Homebrew varsa `brew install --cask docker`; yoksa işlemcinize uygun (Apple Silicon / Intel) resmi `.dmg` indirilir | Parolanız istenebilir. Docker Desktop ilk açılışta lisans onayı isteyebilir. |
| Linux | Docker'ın resmi `get.docker.com` betiği (`sudo` ile) | `curl` gerekir. Kullanıcınız `docker` grubuna eklenir; bu oturumda komutlar `sudo` ile çalışır, sonraki oturumdan itibaren gerekmez. |

İlk açılış imajlar indirildiği için birkaç dakika sürebilir; sonraki açılışlar saniyeler içindedir.

## Adresler ve giriş bilgileri

| Ne | Adres |
| --- | --- |
| Site | http://localhost:5173 |
| Admin paneli | http://localhost:5173/admin |
| API belgeleri (Swagger) | http://localhost:8000/api/docs/ |
| API belgeleri (ReDoc) | http://localhost:8000/api/redoc/ |
| PostgreSQL (makineden) | `localhost:5433`, veritabanı/kullanıcı/parola: `yanimda` |

Yerel geliştirme için admin hesabı otomatik oluşturulur:

- E-posta: `admin@yanimda.local`
- Parola: `Yanimda-Admin-2026`

> Bu bilgiler yalnızca kendi bilgisayarınızda geliştirme içindir; üretimde kullanılmamalıdır.

Son kullanıcı hesabı için siteden kayıt olun. Varsayılan hizmet türleri (evde bakım, refakat, hastane eşliği, alışveriş ve ev işleri, sağlık takibi, küçük ev tamiri) ilk açılışta otomatik yüklenir.

## Durdurma ve sıfırlama

- **Durdurmak:** `stop-*` betikleri veya `docker compose down`. Veriler korunur.
- **Tüm veriyi silip sıfırdan başlamak:** `docker compose down -v` ve ardından başlatma betiği.
- **Logları görmek:** `docker compose logs -f backend` (veya `frontend`, `db`).

## Mimari

```
yanimda/
├── backend/               Django + DRF API
│   ├── apps/accounts/     Kullanıcı, kayıt, JWT, admin kullanıcı API'si
│   ├── apps/care/         Hizmet türleri, başvurular, admin talep ve istatistik API'si
│   ├── config/            Ayarlar, URL'ler, proje düzeyi testler
│   └── locale/            Türkçe çeviriler
├── frontend/              Vue 3 + Vite
│   ├── src/api/           axios istemcisi, token saklama, API çağrıları
│   ├── src/layouts/       PublicLayout (son kullanıcı) ve AdminLayout (yönetim)
│   ├── src/router/        Route'lar ve guard'lar
│   ├── src/stores/        Pinia store'ları
│   ├── src/styles/        Son kullanıcı görsel dili
│   ├── src/views/         public/ ve admin/ sayfaları
│   └── tests/             Türlerine göre testler
├── scripts/               Başlatma/durdurma betikleri ve testleri
├── docker-compose.yml     Tüm yığın
└── prd.md                 Ürün gereksinimleri
```

### Servisler ve açılış sırası

| Servis | İmaj | Port | Sağlıklı sayılma koşulu |
| --- | --- | --- | --- |
| `db` | postgres:17-alpine | 5433 → 5432 | `pg_isready` |
| `backend` | python:3.12-slim | 8000 | migration, varsayılan veri ve admin hesabı hazır, `/api/services/` yanıt veriyor |
| `frontend` | node:22-alpine | 5173 | Vite geliştirme sunucusu yanıt veriyor |

`depends_on: condition: service_healthy` ile sıra garanti edilir: **db → backend → frontend**. Backend açılışta sırasıyla çevirileri derler, migration'ları uygular, varsayılan hizmetleri yükler (`care_create_defaults`, tekrar çalıştırılabilir) ve admin hesabını (yoksa) oluşturur. Kaynak kod klasörleri konteynerlere bağlıdır; değişiklikler anında yansır.

Frontend, `/api` isteklerini Vite proxy'si ile backend'e iletir; tarayıcı yalnızca `localhost:5173` ile konuşur.

### Teknolojiler

| Katman | Teknoloji |
| --- | --- |
| Backend | Python 3.12, Django 5.2, Django REST Framework, Simple JWT (token kara listesi ile), drf-spectacular, django-filter, django-environ |
| Veritabanı | PostgreSQL 17 (SQLite kullanılmaz) |
| Frontend | Vue 3 (`<script setup>`), Vue Router, Pinia, axios, Vite |
| Admin arayüzü | PrimeVue (yalnızca admin tarafında, ayrı yüklenen paketlerde) |
| Testler | Django test runner, Vitest + Vue Test Utils + axe-core, Playwright imajı ile ekran görüntüsü kontrolleri |

### İki ayrı arayüz

- **Son kullanıcı** (`PublicLayout`): PrimeVue ve tablo/dashboard bileşenleri kullanılmaz. Sıcak, fotoğraflı, tam genişlik bir hizmet sitesi: beyaz zemin, açık adaçayı ve şeftali tonlu bölümler, koyu çam yeşili ana renk (`#1F5F55`), kayısı vurgu rengi (`#F29E4C`), koyu yeşil alt bilgi. Başlıklarda **Bricolage Grotesque**, gövdede az görenler için tasarlanmış **Atkinson Hyperlegible Next**; temel yazı boyutu 19 px, dokunma alanları geniş tutulur (en az 44 px). Yapışkan üst bar mobilde açılır menüye dönüşür. Klavye odağı her zaman görünür, "İçeriğe geç" bağlantısı vardır, azaltılmış hareket tercihi desteklenir. Fotoğraflar Pexels lisanslıdır; kaynakları `frontend/public/images/CREDITS.md` dosyasındadır ve aynı adlarla kendi fotoğraflarınızla değiştirilebilir.
- **Admin** (`AdminLayout`): kenar çubuğu, üst bar, tablo, filtre, dialog. Tüm admin sayfaları ayrı (lazy) paketlerde yüklenir.

## İş kuralları

### Hesaplar

- Giriş **yalnızca e-posta ve parola** ile yapılır; kullanıcı adı kavramı yoktur.
- Bir e-posta adresi **tek bir hesaba** aittir. Karşılaştırma büyük/küçük harf ve baş/son boşluklardan bağımsızdır (`Ayse@Example.com` = `ayse@example.com`). E-posta küçük harfle saklanır; girişte nasıl yazıldığı fark etmez.
- Parola Django'nun parola kurallarına uymalıdır (en az 8 karakter, çok yaygın olmayan, yalnız rakam olmayan, kişisel bilgilere benzemeyen).
- Profilde yalnızca ad, soyad ve telefon değiştirilebilir; e-posta ve admin yetkisi değiştirilemez.
- Admin yetkisi (`is_staff`) kayıt veya profil üzerinden alınamaz.
- Pasif yapılan hesap açık oturumu dahil anında erişimini kaybeder.
- Hatalı parola ile kayıtlı olmayan e-posta aynı hatayı verir (hangi e-postanın kayıtlı olduğu anlaşılamaz).

### Oturum (JWT)

- Access token 15 dakika, refresh token 7 gün geçerlidir.
- Refresh token her yenilemede **döndürülür** ve eskisi **kara listeye** alınır; tekrar kullanılamaz.
- Çıkış yapıldığında refresh token sunucuda kara listeye alınır. Sunucuya ulaşılamasa bile tarayıcıdaki oturum temizlenir.
- Frontend, süresi dolan access token'ı bir kez otomatik yeniler; aynı anda gelen 401 yanıtları tek yenileme isteğini paylaşır. Token yalnızca kendi API'mize gönderilir.
- Giriş sonrası yönlendirme yalnızca uygulama içi yollara yapılır (açık yönlendirme engeli).

### Başvurular

- Başvuru için giriş ve **kişisel veri işleme onayı** zorunludur; onay zamanı kaydedilir.
- Tercih edilen tarih bugünden önce olamaz, bugünden en fazla 90 gün sonrası olabilir.
- Yaşlının yaşı 40–120 arasında olmalıdır.
- Telefonlar 10–15 rakam olmalıdır; boşluk, parantez ve tireler temizlenerek saklanır.
- Alternatif kişi adı ve telefonu birlikte verilmelidir.
- Yalnızca aktif hizmetlere başvurulabilir. Yayından kaldırılan hizmetin eski başvuruları görünmeye devam eder.
- **Mükerrer başvuru engeli:** Aynı kullanıcı, **aynı yaşlı için aynı hizmete** açık (yeni / inceleniyor / atandı) bir başvurusu varken yenisini açamaz. Talep tamamlanınca veya iptal edilince tekrar başvurabilir. Aynı kişi annesi ve babası için ayrı ayrı veya aynı yaşlı için farklı hizmetlere başvurabilir. Yaşlı adı büyük/küçük harf, fazla boşluk ve Türkçe **I/İ/ı/i** farklarından bağımsız karşılaştırılır ("FATMA YILMAZ" = "fatma yilmaz"). Kural veritabanında kısmi benzersizlik kısıtıyla da korunur; aynı anda gelen iki istek de engellenir.
- Kullanıcı yalnızca **kendi** başvurularını görür; başkasının başvurusu "bulunamadı" (404) döner.
- Kullanıcı başvurusunu değiştiremez veya silemez. **Yönetici notu** kullanıcıya hiçbir zaman gösterilmez.
- Kullanıcı başına günde en fazla 20 başvuru oluşturulabilir.

### Durum akışı

```
yeni ──► inceleniyor ──► atandı ──► tamamlandı
  │            │             │
  └────────────┴─────────────┴────► iptal edildi
```

- Adımlar atlanamaz, geri gidilemez. Tamamlandı ve iptal edildi son durumlardır.
- Aynı durumu tekrar göndermek serbesttir; böylece yalnızca yönetici notu güncellenebilir.
- Admin, başvurudaki kişisel bilgileri değiştiremez; yalnızca durum ve yönetici notu (en fazla 2000 karakter) güncellenir.

### Admin

- Admin API'leri ve sayfaları yalnızca `is_staff` kullanıcılara açıktır. Django'nun kendi yönetim paneli kullanılmaz ve yayında değildir.
- Gösterge paneli: toplam, açık ve son 7 günlük başvuru sayısı; aktif başvuru sahibi sayısı; her durumun ve her hizmetin sayısı (sıfırlar dahil); son 14 günün günlük serisi.
- Kullanıcı yönetimi şimdilik salt okunurdur.

## API

Tüm uç noktalar `/api/` altındadır. Ayrıntılı alan açıklamaları ve deneme ekranı için Swagger'ı kullanın: http://localhost:8000/api/docs/ (sağ üstteki **Authorize** ile `Bearer <access>` girin).

| Yöntem | Yol | Erişim | Açıklama |
| --- | --- | --- | --- |
| POST | `/api/auth/register/` | Herkes | Kayıt |
| POST | `/api/auth/token/` | Herkes | Giriş (access + refresh) |
| POST | `/api/auth/token/refresh/` | Herkes | Token yenileme |
| POST | `/api/auth/logout/` | Herkes | Çıkış (refresh token'ı kara listeye alır) |
| GET, PATCH | `/api/auth/me/` | Giriş yapmış | Profil |
| GET | `/api/services/` | Herkes | Aktif hizmetler (sayfalanmaz) |
| GET, POST | `/api/requests/` | Giriş yapmış | Kendi başvurularım / yeni başvuru |
| GET | `/api/requests/{id}/` | Giriş yapmış | Kendi başvurumun detayı |
| GET | `/api/admin/stats/` | Admin | Gösterge paneli istatistikleri |
| GET | `/api/admin/requests/` | Admin | Tüm başvurular; `status`, `service`, `applicant`, `created_from`, `created_to`, `search`, `ordering` |
| GET, PATCH | `/api/admin/requests/{id}/` | Admin | Detay; durum ve yönetici notu güncelleme |
| GET | `/api/admin/users/` | Admin | Kullanıcılar ve başvuru sayıları; `is_staff`, `is_active`, `search`, `ordering` |
| GET | `/api/admin/users/{id}/` | Admin | Kullanıcı detayı |
| GET | `/api/schema/`, `/api/docs/`, `/api/redoc/` | Herkes (yalnızca `API_DOCS_ENABLED`) | OpenAPI şeması ve belgeler |

Listeler 20'şerli sayfalanır: `{count, next, previous, results}`. Hata mesajları istek diline göre Türkçe veya İngilizce döner (`Accept-Language`).

## Ayarlar

Backend ayarları ortam değişkenlerinden okunur. Örnek dosya: `backend/.env.example` (Docker dışında çalışırken `backend/.env` olarak kopyalayın). Docker'da değerler `docker-compose.yml` içindedir.

| Değişken | Varsayılan | Açıklama |
| --- | --- | --- |
| `SECRET_KEY` | geliştirme anahtarı | Django gizli anahtarı; üretimde mutlaka değiştirin |
| `DEBUG` | `False` | Hata ayıklama modu |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | İzin verilen host'lar |
| `DATABASE_URL` | `postgres://yanimda:yanimda@localhost:5433/yanimda` | PostgreSQL bağlantısı |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Frontend kaynakları |
| `API_DOCS_ENABLED` | `DEBUG` değeri | Şema, Swagger ve ReDoc'u yayınlar |
| `JWT_ACCESS_MINUTES` | `15` | Access token ömrü (dakika) |
| `JWT_REFRESH_DAYS` | `7` | Refresh token ömrü (gün) |
| `CARE_MAX_PREFERRED_DAYS_AHEAD` | `90` | Tercih edilen tarihin en ileri gün sayısı |
| `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` | — | Verilirse açılışta (yoksa) admin hesabı oluşturulur |

### Hız sınırları (throttle)

| Amaç | Scope | Varsayılan | Ortam değişkeni |
| --- | --- | --- | --- |
| Kayıt (IP başına) | `accounts_register` | `10/hour` | `THROTTLE_ACCOUNTS_REGISTER` |
| Giriş (IP başına) | `accounts_login` | `10/minute` | `THROTTLE_ACCOUNTS_LOGIN` |
| Başvuru oluşturma (kullanıcı başına) | `care_request_create` | `20/day` | `THROTTLE_CARE_REQUEST_CREATE` |

Proje ayarlarından ezmek için:

```python
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'accounts_register': '10/hour',
    'accounts_login': '10/minute',
    'care_request_create': '20/day',
}
```

Frontend için `VITE_API_PROXY_TARGET` (varsayılan `http://localhost:8000`) ve Windows'taki bağlı klasörlerde dosya izleme için `VITE_USE_POLLING=true` kullanılır.

## Testler

Testler türlerine göre klasörlenmiştir ve her değişiklikten önce tamamı regresyon olarak çalıştırılır. Testler **Docker konteynerlerinde, PostgreSQL üzerinde** çalışır.

### Backend (150 test)

| Tür | Klasör | Ne sınar |
| --- | --- | --- |
| `unit` | `apps/*/tests/unit` | Model kuralları, durum geçişleri, doğrulayıcılar, ad anahtarı, throttle ayarları |
| `integration` | `apps/*/tests/integration`, `config/tests/integration` | Uç noktaların davranışı, filtre/arama/sıralama, varsayılan veri komutu, Swagger |
| `security` | `apps/*/tests/security`, `config/tests/security` | Yetkisiz erişim, başkasının verisine erişim (IDOR), toplu atama, yetki yükseltme, token yeniden kullanımı, hız sınırları, veri sızıntısı |
| `regression` | `apps/*/tests/regression`, `config/tests/regression` | Bulunmuş hataların geri gelmemesi, eksik migration, PostgreSQL zorunluluğu, Django admin'in kapalı olması |
| `contract` | `apps/*/tests/contract`, `config/tests/contract` | Frontend'in bağlı olduğu yanıt şekilleri, OpenAPI şemasının uyarısız geçerliliği |
| `performance` | `apps/*/tests/performance` | Listelerde N+1 sorgu olmaması, sabit sorgu sayısı |
| `scenario` | `config/tests/scenario` | Gerçek kayıt/giriş ile uçtan uca iş akışları: tek e-posta tek hesap, e-postayla giriş, mükerrer başvuru, tam yaşam döngüsü, aile ayrımı, gösterge paneli |

```bash
docker compose exec backend sh run_tests.sh              # hepsi
docker compose exec backend sh run_tests.sh security     # tek tür
docker compose exec backend sh run_tests.sh unit scenario
```

### Frontend (147 test)

| Tür | Klasör | Ne sınar |
| --- | --- | --- |
| `unit` | `tests/unit` | Route tablosu, token saklama, güvenli yönlendirme |
| `component` | `tests/component` | Bileşen davranışı (ör. oturuma göre menü) |
| `integration` | `tests/integration` | HTTP istemcisi ve token yenileme, auth store, yönlendirme |
| `security` | `tests/security` | Route guard'ları, token'ın dış adrese gitmemesi, açık yönlendirme |
| `accessibility` | `tests/accessibility` | axe-core denetimi, içeriğe geç bağlantısı, sayfa bölgeleri |

```bash
docker compose exec frontend npx vitest run
docker compose exec frontend npx vitest run tests/security
```

### Başlatma betikleri

Betikler gerçek kurulum yapmadan, çağrıları kaydeden sahte komutlarla test edilir.

```bash
# macOS ve Linux akışları (30 kontrol) — Docker olan her sistemde
docker run --rm -v "$PWD:/src:ro" ubuntu:24.04 bash /src/scripts/tests/start-unix.test.sh
```

```powershell
# Windows akışı (20 kontrol) — Windows PowerShell 5.1 veya PowerShell 7
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\tests\start-windows.tests.ps1
```

## Betikler olmadan geliştirme

```bash
docker compose up -d --build --wait          # tüm yığın, sırayla
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py care_create_defaults
docker compose exec backend python manage.py createsuperuser
```

Yeni paket ekledikten sonra imajı yenileyin: `docker compose up -d --build -V frontend` (`-V`, eski `node_modules` birimini yeniler).

### Çeviriler

Kullanıcıya görünen backend metinleri İngilizce yazılır ve `gettext` ile işaretlenir; Türkçesi `backend/locale/tr/LC_MESSAGES/django.po` dosyasındadır.

```bash
python manage.py makemessages -l tr -e py -e html -e json -i "venv/*" --no-location
python manage.py compilemessages -l tr
```

`.mo` dosyaları depoya eklenmez; konteyner açılışında derlenir.

## Güvenlik notları

- `docker-compose.yml` içindeki parola ve anahtarlar yalnızca yerel geliştirme içindir.
- Üretimde `DEBUG=False`, güçlü `SECRET_KEY`, gerçek `ALLOWED_HOSTS` kullanın ve `DJANGO_SUPERUSER_*` değişkenlerini kaldırın. `API_DOCS_ENABLED` varsayılan olarak `DEBUG`'u izler; üretimde belgeler kapalıdır.
- Tarayıcı token'ları `localStorage`'da tutar; access token kısa ömürlüdür ve refresh token'lar döndürülüp kara listeye alınır.

## Git akışı

- Git Flow kullanılır: yeni özellikler `feature/*`, hata düzeltmeleri `hotfix/*` dallarında geliştirilir; `develop` ve `master` dallarına doğrudan yazılmaz.
- Commit'ler küçük, anlamlı ve her biri kendi başına çalışır durumdadır; her commit'ten önce tüm testler çalıştırılır.
- Commit mesajları önce İngilizce, sonra Türkçe özet ve maddelerden oluşur.

## Sorun giderme

| Belirti | Çözüm |
| --- | --- |
| Windows: "Docker 4 dakika içinde hazır olmadı" | İlk kurulumdan sonra bilgisayarı yeniden başlatın (WSL 2), Docker Desktop'ı bir kez elle açıp şartları onaylayın, betiği tekrar çalıştırın. |
| macOS: Docker başlamıyor | Docker Desktop'ı Uygulamalar'dan açıp lisansı onaylayın, betiği tekrar çalıştırın. |
| Linux: `permission denied ... docker.sock` | Oturumu kapatıp açın (docker grubu), ya da komutları `sudo` ile çalıştırın. |
| Port kullanımda (5173, 8000, 5433) | O portu kullanan uygulamayı kapatın veya `docker-compose.yml` içindeki sol taraftaki port numarasını değiştirin. |
| Site açılıyor ama veri gelmiyor | `docker compose ps` ile servislerin `healthy` olduğunu, `docker compose logs backend` ile hataları kontrol edin. |
| Frontend'de yeni paket bulunamıyor | `docker compose up -d --build -V frontend` |
| Her şeyi sıfırlamak | `docker compose down -v` ve başlatma betiği |
