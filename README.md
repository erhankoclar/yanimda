# Yanımda

[English](README.en.md)

Yanımda, yaşlı yakını için evde bakım, refakat, hastane eşliği gibi hizmetlere başvuru yapan aileler ile bu başvuruları yöneten ekip için geliştirilen bir web uygulamasıdır.

- **Son kullanıcı arayüzü:** sıcak, fotoğraflı, mobil öncelikli hizmet sitesi. Hesap açmadan doldurulan **hızlı talep formu** (ad, e-posta, hizmet, açıklama) ve hesapla yapılan, takip edilebilen **5 adımlı başvuru** içerir.
- **Admin paneli:** talepleri, kullanıcıları ve istatistikleri yöneten yoğun bilgi ekranları (PrimeVue).
- **API:** Django REST Framework, PostgreSQL, JWT kimlik doğrulama.

> **Durum:** Backend API'nin tamamı, son kullanıcı arayüzü, tek tıkla çalıştırma ve Render yayın yapılandırması hazırdır. Admin panel **ekranları** yapılmadı (API'leri hazır); bkz. [Bilinen eksikler](#bilinen-eksikler).

## Teslim

| | |
| --- | --- |
| Canlı adres | _Render yayınından sonra eklenecek_ |
| Kaynak kod | https://github.com/erhankoclar/yanimda |
| Teslim commit'i | _Sürüm etiketinden sonra eklenecek_ |
| Yapay zekâ kullanım kaydı | [AI_LOG.md](AI_LOG.md) |

Değerlendirme kriterlerinin karşılandığı yerler:

| Kriter | Nerede |
| --- | --- |
| Mobil ve masaüstü uyumlu landing page | Ana sayfa (`frontend/src/views/public/LandingView.vue`); e2e testleri telefon ve masaüstünde koşar |
| İsim, e-posta, hizmet seçimi ve açıklama içeren form | Ana sayfadaki "Talebinizi bırakın" formu (`InquiryForm.vue`) |
| İstemci ve sunucu tarafında alan doğrulaması | `frontend/src/utils/inquiryValidation.js` ve `backend/apps/care/inquiry_serializers.py` |
| Gönderiliyor, başarı ve hata durumları | Düğmede "Gönderiliyor…" yazar ve form kilitlenir; kayıt numaralı başarı mesajı; alan ve genel hata mesajları |
| Kaydın sunucuda kalıcı saklanması | PostgreSQL `care_serviceinquiry` tablosu; `GET /api/admin/inquiries/` ile görülebilir |
| Başarı mesajı yalnızca kayıt başarılıysa | Mesaj yalnızca sunucu kaydı (kimliğiyle) döndürünce gösterilir; 4xx, 5xx, ağ hatası ve kimliksiz yanıtlar için testler var |
| README, AI_LOG.md, teslim commit'i | Bu dosya, [AI_LOG.md](AI_LOG.md), yukarıdaki tablo |

## İçindekiler

- [Teslim](#teslim)
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
- [Canlı yayın (Render)](#canlı-yayın-render)
- [Git akışı](#git-akışı)
- [Bilinen eksikler](#bilinen-eksikler)
- [Kaynaklar ve şablonlar](#kaynaklar-ve-şablonlar)
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

### Backend katmanları

| Katman | Sorumluluk |
| --- | --- |
| `services/*_service.py` | Tüm iş akışları **ve okuma işlemleri** (ör. `care_request_service.create_request`, `list_for_admin`, `dashboard_service.build_dashboard`). Celery task'ı eklenirse ilgili servis dosyasında, sınıf dışında tanımlanır. |
| `managers.py` | Yalnızca queryset döndüren metotlar (`active()`, `open()`, `waiting_for_review()`, `with_request_count()`). Servisler modellere bu manager'lar üzerinden erişir; manager servisleri modül düzeyinde içe aktarmaz. Django'nun zorunlu kancaları (`create_user`, `create_superuser`, `get_by_natural_key`) servise yönlendirir. |
| `serializers.py` | Yalnızca doğrulama ve yanıt biçimi; `create`/`update` içermez. İş kuralı kontrolleri için servise sorar. |
| `views.py` | İzin, throttle, filtre ve sayfalama; okumayı ve kaydetmeyi servise devreder, servisin iş kuralı hatalarını 400 yanıtına çevirir. |

Kurallar `config/tests/regression/test_architecture.py` ile korunur: bir serializer `create`/`update` tanımlarsa, bir view veya serializer ORM sorgusu kurarsa ya da bir manager servisleri içe aktarırsa test başarısız olur.

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
| Admin arayüzü | PrimeVue (yalnızca admin tarafında, ayrı yüklenen paketlerde), Chart.js |
| Harita | MapLibre GL JS, OpenFreeMap altlığı, OpenStreetMap ilçe/mahalle sınırları |
| İçerik çevirisi | django-parler (yalnızca sistemin sunduğu hizmet türleri) |
| Test ve demo verisi | factory-boy + Faker |
| Testler | Django test runner, Vitest + Vue Test Utils + axe-core, Playwright imajı ile ekran görüntüsü kontrolleri |

### İki ayrı arayüz

- **Son kullanıcı** (`PublicLayout`): PrimeVue ve tablo/dashboard bileşenleri kullanılmaz. Sıcak, fotoğraflı, tam genişlik bir hizmet sitesi: beyaz zemin, açık adaçayı ve şeftali tonlu bölümler, koyu çam yeşili ana renk (`#1F5F55`), kayısı vurgu rengi (`#F29E4C`), koyu yeşil alt bilgi. Başlıklarda **Bricolage Grotesque**, gövdede az görenler için tasarlanmış **Atkinson Hyperlegible Next**; temel yazı boyutu 19 px, dokunma alanları geniş tutulur (en az 44 px). Yapışkan üst bar mobilde açılır menüye dönüşür. Klavye odağı her zaman görünür, "İçeriğe geç" bağlantısı vardır, azaltılmış hareket tercihi desteklenir. Fotoğraflar Pexels lisanslıdır; kaynakları `frontend/public/images/CREDITS.md` dosyasındadır ve aynı adlarla kendi fotoğraflarınızla değiştirilebilir.
- **Admin** (`AdminLayout`): kenar çubuğu, üst bar, tablo, filtre, dialog. Tüm admin sayfaları ayrı (lazy) paketlerde yüklenir.

## İş kuralları

### Hızlı talep formu (hesapsız)

- Ad soyad (en az 2 karakter), geçerli e-posta, aktif bir hizmet, 10–2000 karakter açıklama ve kişisel veri onayı zorunludur. Kurallar istemci ve sunucuda aynıdır; sunucu her zaman yeniden doğrular.
- Gönderim sırasında düğme "Gönderiliyor…" olur ve alanlar kilitlenir. Başarı mesajı **yalnızca** sunucu kaydı saklayıp kayıt numarasını döndürdüğünde gösterilir. Hata olursa yazılanlar korunur; alan hataları alanın altında, diğer hatalar formun üstünde görünür.
- E-posta küçük harfle, ad fazla boşluklar temizlenerek saklanır; onay zamanı kaydedilir.
- Spam botlarına karşı görünmez bir tuzak alanı vardır ve istekler IP başına saatte 5 ile sınırlıdır.
- Ana sayfadaki hizmet kartları formu ilgili hizmet seçili olarak açar.

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
- **Konum:** Hizmet yalnızca İstanbul'da verilir. İlçe ve mahalle listeden seçilir (OpenStreetMap sınırları, 39 ilçe, 964 mahalle); adres alanına sokak, bina ve daire yazılır. Hızlı talep formunda da ilçe ve mahalle sorulur. Konum alınmaya başlanmadan önceki kayıtlarda il/ilçe metni adresin sonuna taşınmıştır ve haritada yer almaz.
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
- **Talep haritası** (`/admin/map`): İstanbul'un tematik haritası. Uzaktan bakınca il toplamı tek balon olarak görünür; yakınlaştıkça önce ilçe, sonra mahalle sayıları açılır (en ayrıntılı düzey mahalledir). Alanlar sayıya göre tek tonlu yoğunluk rengiyle boyanır; lejant sınıfları verinin dağılımından hesaplanır. Toplam ya da tek hizmet, kaynak (hızlı talep / başvuru) ve dönem seçilebilir. Yandaki sıralama en çok ve hiç talep gelmeyen yerleri gösterir; bir sayıya, alana ya da satıra tıklayınca o yerin kayıtları yan panelde listelenir.
- **Admin girişi:** `/admin/login` ya da sitenin genel giriş sayfası. Yönetici hesabıyla genel girişten girilince doğrudan yönetim paneli açılır; oturum açıkken sitenin üst barında "Yönetim paneli" bağlantısı görünür. Yönetici olmayan hesap admin girişinden girerse uyarılır ve oturumu kapatılır.
- **Listeler:** Hızlı talepler (arama, hizmet ve ilçe süzgeci; ayrıntı paneli ve "e-posta ile yanıtla"), başvurular (arama, durum, hizmet, ilçe, tarih aralığı; sıralama) ve kullanıcılar (arama, rol, hesap durumu; sıralama). Süzgeçler, sayfa ve sıralama adres çubuğunda tutulur; geri tuşu ve paylaşılan bağlantı aynı listeyi açar.
- **Başvuru detayı:** Durum yalnızca izin verilen sonraki durumlara, onay penceresiyle değiştirilir; yönetici notu buradan yazılır.
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
| POST | `/api/inquiries/` | Herkes | Hızlı talep formu (hesapsız) |
| GET, POST | `/api/requests/` | Giriş yapmış | Kendi başvurularım / yeni başvuru |
| GET | `/api/requests/{id}/` | Giriş yapmış | Kendi başvurumun detayı |
| GET | `/api/admin/stats/` | Admin | Gösterge paneli istatistikleri |
| GET | `/api/admin/inquiries/` | Admin | Hızlı talepler; `service`, `search` |
| GET | `/api/admin/requests/` | Admin | Tüm başvurular; `status`, `service`, `applicant`, `created_from`, `created_to`, `search`, `ordering` |
| GET, PATCH | `/api/admin/requests/{id}/` | Admin | Detay; durum ve yönetici notu güncelleme |
| GET | `/api/admin/users/` | Admin | Kullanıcılar ve başvuru sayıları; `is_staff`, `is_active`, `search`, `ordering` |
| GET | `/api/admin/users/{id}/` | Admin | Kullanıcı detayı |
| GET | `/api/schema/`, `/api/docs/`, `/api/redoc/` | Herkes (yalnızca `API_DOCS_ENABLED`) | OpenAPI şeması ve belgeler |

Listeler 20'şerli sayfalanır: `{count, next, previous, results}`. Hata mesajları istek diline göre Türkçe veya İngilizce döner (`Accept-Language`). Sistemin sunduğu içerik olan hizmet türlerinin ad ve açıklamaları [django-parler](https://github.com/django-parler/django-parler) ile dil başına bir satırda tutulur ve aynı başlığa göre döner; çevirisi olmayan dilde Türkçeye düşülür. Vatandaşın girdiği başvuru ve hızlı talepler çevrilmez, girildiği dilde saklanır.

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
| `TEST_USER_PASSWORD` | `Yanimda-Guclu-2026` | Testlerdeki fabrikaların kurgusal hesaplara yazdığı parola |
| `DEMO_USER_PASSWORD` | `Kurgusal-Demo-2026` | `care_create_demo_data` komutunun demo hesaplarına yazdığı parola |

### Hız sınırları (throttle)

| Amaç | Scope | Varsayılan | Ortam değişkeni |
| --- | --- | --- | --- |
| Kayıt (IP başına) | `accounts_register` | `10/hour` | `THROTTLE_ACCOUNTS_REGISTER` |
| Giriş (IP başına) | `accounts_login` | `10/minute` | `THROTTLE_ACCOUNTS_LOGIN` |
| Başvuru oluşturma (kullanıcı başına) | `care_request_create` | `20/day` | `THROTTLE_CARE_REQUEST_CREATE` |
| Hızlı talep formu (IP başına) | `care_inquiry_create` | `5/hour` | `THROTTLE_CARE_INQUIRY_CREATE` |

Proje ayarlarından ezmek için:

```python
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'accounts_register': '10/hour',
    'accounts_login': '10/minute',
    'care_request_create': '20/day',
    'care_inquiry_create': '5/hour',
}
```

Yerel `docker-compose.yml` ortamında e2e testleri tek IP'den çok istek attığı için bu sınırlar gevşetilmiştir; üretimde (Render) yukarıdaki varsayılanlar geçerlidir.

Frontend için `VITE_API_PROXY_TARGET` (varsayılan `http://localhost:8000`) ve Windows'taki bağlı klasörlerde dosya izleme için `VITE_USE_POLLING=true` kullanılır.

## Testler

Testler türlerine göre klasörlenmiştir ve her değişiklikten önce tamamı regresyon olarak çalıştırılır. Testler **Docker konteynerlerinde, PostgreSQL üzerinde** çalışır.

### Backend (169 test)

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

### Frontend (170 test)

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

### Uçtan uca (Playwright, 18 test)

`e2e/` klasöründeki testler çalışan yığına (gerçek frontend, backend ve PostgreSQL) karşı telefon ve masaüstü görünümlerinde koşar: hızlı formun gönderiliyor/başarı/hata durumları ve kaydın veritabanında bulunması, istemci atlatıldığında sunucu doğrulaması, kayıt + 5 adımlı başvuru + mükerrer başvurunun reddi, yatay taşma ve konsol hatası kontrolü.

```bash
docker compose up -d --wait
docker compose --profile e2e run --rm e2e
# Başka bir adrese karşı (ör. üretim imajı):
docker compose --profile e2e run --rm -e E2E_BASE_URL=https://ornek.onrender.com e2e
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

### Geliştirme betikleri

Tekrarlayan işler `scripts/dev/` altındaki betiklerle yapılır; uzun çıktılar `.dev-logs/` klasörüne yazılır, ekrana yalnızca özet gelir.

| Betik | İş |
| --- | --- |
| `scripts/dev/check-all.sh [--no-e2e]` | Backend, frontend ve e2e testlerinin tamamı (commit öncesi regresyon) |
| `scripts/dev/test-backend.sh [tür...]` | Backend testleri (ör. `unit security`) |
| `scripts/dev/test-frontend.sh [yol...]` | Vitest testleri |
| `scripts/dev/test-e2e.sh [adres]` | Playwright testleri; adres verilirse oraya karşı |
| `scripts/dev/screenshots.sh <ad> <none/applicant/admin> <yol...>` | 390/820/1366 px ekran görüntüleri `.shots/<ad>/` altına; yatay taşma ve konsol hatası raporu |
| `scripts/dev/translations.sh [ceviriler.json]` | Çeviri kataloğunu yeniler, JSON'dan doldurur, eksikleri listeler (`pip install -r backend/requirements-dev.txt`) |

## Betikler olmadan geliştirme

```bash
docker compose up -d --build --wait          # tüm yığın, sırayla
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py care_create_defaults
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py care_create_demo_data   # yalnızca DEBUG; --days 90, --reset
```

`care_create_demo_data`, gösterge panelini anlamlı görmek için son günlere yayılmış kurgusal başvuru sahipleri, hızlı talepler ve başvurular üretir. Kayıtları factory-boy fabrikaları (`apps/*/factories.py`), adları Faker üretir; tüm demo e-postaları ayrılmış `demo.yanimda.example` alan adındadır ve `--reset` yalnızca bunları silip yeniden üretir. `DEBUG` kapalıyken çalışmaz.

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

## Canlı yayın (Render)

Kök dizindeki `Dockerfile` Vue sitesini derler ve Django API ile birlikte tek bir gunicorn servisinden sunar (WhiteNoise). Sayfa adresleri (`/requests/5` gibi) Vue'ya, `/api/` adresleri Django'ya gider.

1. Render'da **New → Blueprint** seçin ve bu GitHub deposunu bağlayın; `render.yaml` okunur.
2. Render ücretsiz PostgreSQL veritabanını ve web servisini oluşturur; `SECRET_KEY` otomatik üretilir.
3. İstendiğinde `DJANGO_SUPERUSER_PASSWORD` için güçlü bir parola girin (admin e-postası: `admin@yanimda.example`).
4. Yayın bitince adres `https://<servis-adı>.onrender.com` olur. Açılışta migration, varsayılan hizmetler ve admin hesabı otomatik hazırlanır.

Üretim notları:
- `DEBUG=False`, HSTS açık, çerezler yalnızca HTTPS'te gönderilir. HTTP'den HTTPS'e yönlendirmeyi Render yapar; uygulamadaki `SECURE_SSL_REDIRECT` kapalı tutulur, çünkü açık olursa Render'ın iç HTTP sağlık kontrolü 301 alıp başarısız olur.
- Swagger değerlendirme için açıktır (`API_DOCS_ENABLED=True`); kapatmak için bu değişkeni `False` yapın.
- Üretim imajını yerelde denemek için: `docker build -t yanimda-prod .` ve `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS` vererek çalıştırın.

## Git akışı

- Git Flow kullanılır: yeni özellikler `feature/*`, hata düzeltmeleri `hotfix/*` dallarında geliştirilir; `develop` ve `master` dallarına doğrudan yazılmaz.
- Commit'ler küçük, anlamlı ve her biri kendi başına çalışır durumdadır; her commit'ten önce tüm testler çalıştırılır.
- Commit mesajları önce İngilizce, sonra Türkçe özet ve maddelerden oluşur.

## Bilinen eksikler

- Harita altlığı OpenFreeMap'in ücretsiz hizmetinden gelir; hizmete erişilemezse harita açılmaz; sıralama listesi ve kayıt listeleri haritadan bağımsız çalışmayı sürdürür.
- Hızlı talep gelince e-posta bildirimi gönderilmez; talepler kaydedilir ve admin API'sinden görülür.
- Başvurular internetten düzenlenemez veya iptal edilemez.
- İletişim telefonu ve çalışma saatleri yer tutucudur.
- Render ücretsiz katmanında servis boşta uyur (ilk istek yaklaşık 30 sn sürer) ve ücretsiz PostgreSQL 30 gün sonra silinir.
- macOS ve Linux başlatma betikleri sahte komutlarla test edildi, gerçek bir macOS/Linux makinesinde denenmedi.

## Kaynaklar ve şablonlar

- Hazır proje şablonu (boilerplate) kullanılmadı. Django iskeleti `django-admin startproject/startapp` ile oluşturuldu; Vite yapılandırması elle yazıldı. Geri kalan kod bu proje için yazıldı.
- Kod yapay zekâ (Claude Code) ile, geliştiricinin kararları ve yönlendirmeleriyle üretildi; ayrıntılar [AI_LOG.md](AI_LOG.md) dosyasında.
- Fotoğraflar: Pexels lisanslı stok fotoğraflar; kaynakları `frontend/public/images/CREDITS.md` dosyasında.
- Yazı tipleri: Google Fonts üzerinden Atkinson Hyperlegible Next ve Bricolage Grotesque (SIL Open Font License).
- Kullanılan açık kaynak kütüphaneler: `backend/requirements.txt`, `frontend/package.json` ve `e2e/package.json`.

### Dış kaynaklar

| Kaynak | Ne için | Lisans | Bağlantı |
| --- | --- | --- | --- |
| OpenStreetMap ilçe ve mahalle sınırları | Konum seçimi ve harita poligonları (`frontend/public/geo`, `backend/apps/geo/data`) | ODbL 1.0, atıf: © OpenStreetMap katkıcıları | https://www.openstreetmap.org/copyright |
| Overpass API | Sınırların indirilmesi (yalnızca `scripts/geo/build_istanbul_boundaries.py`) | Hizmet; veri ODbL | https://overpass-api.de |
| OpenFreeMap | Admin haritasının altlığı (`positron` ve `dark` stilleri, anahtarsız); kesintisiz çalışma garantisi yoktur | Hizmet; veri OpenMapTiles + OpenStreetMap | https://openfreemap.org |
| MapLibre GL JS 6.13.0 | Admin tematik haritası | BSD-3-Clause | https://maplibre.org |
| osmtogeojson 3.0.0-beta.5 | OSM verisini GeoJSON'a çevirme (yalnızca sınır betiği, `npx`) | MIT | https://github.com/tyrasd/osmtogeojson |
| mapshaper 0.6.102 | Sınırları sadeleştirme ve etiket noktaları (yalnızca sınır betiği, `npx`) | MPL-2.0 | https://github.com/mbloch/mapshaper |
| django-parler 2.4 | Hizmet türü ad ve açıklamalarının dil başına çevirisi | Apache-2.0 | https://github.com/django-parler/django-parler |
| factory-boy 3.3.3 + Faker 40.41.0 | Test verisi ve `care_create_demo_data` kurgusal verisi | MIT | https://factoryboy.readthedocs.io |
| PrimeVue 4.5.5, PrimeIcons 7.0.0 | Admin arayüzü | MIT | https://primevue.org |
| Chart.js 4.5.1 | Gösterge paneli grafikleri | MIT | https://www.chartjs.org |
| vue-i18n 11 | Türkçe/İngilizce arayüz | MIT | https://vue-i18n.intlify.dev |

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
