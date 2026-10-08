# AI_LOG — Yanımda

Bu belge, projenin yapay zekâ ile nasıl üretildiğini, hangi kararların kime ait olduğunu ve sonucun nasıl doğrulandığını kayıt altına alır. Bilgiler oturumun kendisinden ve commit geçmişinden (`git log`) alınmıştır; tahmin veya uydurma içermez.

## 1. Süre

- **1. dönem (1.0.0 teslimi):** 2026-10-07 17:09 – 20:32, yaklaşık 3,5 saat. Son kullanıcı sitesi, API, testler, başlatma betikleri, üretim imajı.
- **2. dönem (1.1.0):** 2026-10-08 01:58 – 14:34 arası commit'ler. Bu aralıkta molalar ve worker'ların çalışmasını bekleme süreleri vardır; etkin çalışma süresi ayrıca ölçülmedi. Admin paneli, koyu/açık tema, Türkçe/İngilizce arayüz, konum ve tematik harita.
- Süreler commit zaman damgalarından alınmıştır; PRD'nin yazılması bu sürelerin dışındadır.

## 2. Araçlar

| Araç | Ne için kullanıldı |
| --- | --- |
| **Claude Code** (VS Code eklentisi), model **Claude Opus 5.5** | Planlama, kod yazma, test yazma ve çalıştırma, tarayıcı kontrolleri, commit'ler, belgeler |
| Claude Code kullanıcı becerileri (skills) | Ekibin kurallarını otomatik uygulamak: Git Flow akışı, iki dilli commit mesajı biçimi, Türkçe docstring standardı, Django çeviri kuralları, throttle ayar standardı, API açıklama standardı, iki dilli README standardı |
| Docker Desktop + Docker Compose | Tüm yığın (PostgreSQL, Django, Vite) ve tüm testlerin konteynerde çalıştırılması |
| Playwright (resmî `mcr.microsoft.com/playwright` imajı) | 3 ekran boyutunda ekran görüntüsü, gerçek backend'e karşı uçtan uca akışlar, kalıcı e2e test paketi |
| axe-core | Otomatik erişilebilirlik denetimi |
| shellcheck (Docker imajı) | macOS/Linux başlatma betiklerinin statik denetimi |
| Pexels | Lisansı ticari kullanıma izin veren stok fotoğraflar (`frontend/public/images/CREDITS.md`) |
| GitHub CLI (`gh`) | Uzak deponun durumunu kontrol etmek |
| Claude Code alt ajanları (worker), modeller **Claude Sonnet 5.5** ve **Claude Haiku 4.5** | 2. dönemde test yazma ve çalıştırma, ekran görüntüsü taraması ve tasarım denetimi; ana model yalnızca geliştirme ve sonuçların değerlendirilmesini yaptı |
| PrimeVue MCP sunucusu | PrimeVue bileşen kullanımını yazmadan önce API'ye göre doğrulamak |
| OpenStreetMap + Overpass API, osmtogeojson, mapshaper | İstanbul ilçe ve mahalle sınırlarının üretilmesi (`scripts/geo/build_istanbul_boundaries.py`) |

Hazır bir proje şablonu (boilerplate) kullanılmadı. Django iskeleti `django-admin startproject/startapp` komutlarıyla oluşturuldu, Vite projesi elle kuruldu. Kodun geri kalanı bu oturumda yazıldı.

## 3. Görev dağılımı

| Kim | Sorumluluk |
| --- | --- |
| **Geliştirici (ürün sahibi)** | PRD'yi yazdı; teknoloji ve kapsam kararlarını verdi; ara sonuçları inceleyip yönlendirdi (aşağıdaki liste); tasarım yönünü, görsel kaynağını ve yayın platformunu seçti; GitHub deposunu oluşturdu. |
| **AI (Claude Code, ana model)** | Planı çıkardı, uygulama kodunu yazdı, worker raporlarını okuyup hataları düzeltti, commit'leri attı, belgeleri yazdı. Belirsiz noktalarda seçenek sunup kararı geliştiriciye bıraktı. 1. dönemde testleri de kendisi yazıp çalıştırdı. |
| **Worker ajanlar (2. dönem)** | Geliştiricinin isteğiyle testleri yazdı ve çalıştırdı, ekran görüntüsü ve tasarım denetimi yaptı. Uygulama kodunu değiştirmediler; buldukları hataları dosya ve satırıyla raporladılar. |

## 4. Önemli yönlendirmeler ve etkileri

Geliştiricinin oturum boyunca verdiği yönlendirmeler sırasıyla:

| # | Yönlendirme | AI'nın yaptığı / değişen |
| --- | --- | --- |
| 1 | Backend Django + DRF, aynı repo; JS + Pinia + Vitest; önce iskelet ve çekirdek akış | Plan bu kararlarla yazıldı. |
| 2 | "Git Flow kullan" | Tüm işler `feature/*` dallarında yapıldı, `develop`'a birleştirildi. |
| 3 | "Commit'ler küçük ve anlamlı olsun, her commit çalışır bir kayıt noktası olsun" | Her adım test edilip ayrı commit atıldı; her commit öncesi tüm testler regresyon olarak çalıştırıldı. |
| 4 | "Docker kullanabilirsin" | Docker Compose eklendi; testler konteynerde çalışır hale geldi. |
| 5 | "Birim, regresyon, entegrasyon, güvenlik testleri adım adım; türlere göre ayrı klasörler" | Testler `unit/integration/security/regression` klasörlerine ayrıldı. AI ayrıca `contract`, `performance`, `scenario` (backend) ve `component`, `accessibility` (frontend) türlerini önerip ekledi. |
| 6 | "Django'nun admin panelini kullanmayacağım" | Django admin tamamen kaldırıldı; kapalı olduğunu doğrulayan regresyon testi eklendi. |
| 7 | "Swagger ekle" | Swagger ve ReDoc eklendi; tüm uç noktalar belgelendi; üretimde kapatılabilir hale getirildi. |
| 8 | "SQLite kullanma, PostgreSQL kullan" | SQLite varsayılanı kaldırıldı; PostgreSQL zorunluluğu regresyon testiyle sabitlendi. |
| 9 | "Aynı e-postayla tek kullanıcı, e-postayla giriş, aynı hizmete iki kez başvurulamasın gibi iş akışlarını da test et; senaryoları sen çoğalt" | `scenario` test paketi eklendi. "Aynı hizmete iki kez başvurulamaz" kuralı sistemde yoktu ve eklendi. AI kuralı "aynı kişi, **aynı yaşlı için** aynı hizmete açık başvuru varken yenisini açamaz" diye yorumladı ve kullanıcıya bildirdi; itiraz gelmedi. |
| 10 | "Frontend de Docker'da; tek compose'dan sırayla ayağa kalksın" | Frontend servisi ve sağlık kontrolleri eklendi: veritabanı → backend → frontend. |
| 11 | "Windows, macOS, Linux için çalıştırma dosyaları; Docker yoksa kursun, siteyi açsın; TR ve EN README" | Başlatma/durdurma betikleri ve iki dilli README yazıldı. |
| 12 | "Bu betikleri de test et" | Sahte komutlarla senaryo testleri eklendi: Unix 30 kontrol, Windows 20 kontrol. Windows betiği ayrıca bu makinede gerçekten çalıştırıldı. |
| 13 | "Web sitesi tarafında hiçbir şey yok" | Doğru tespit: AI altyapıya odaklanmış, son kullanıcı sayfaları boş kalmıştı. Ana sayfa, giriş, kayıt, sihirbaz ve başvuru sayfaları yapıldı. |
| 14 | "Bu nasıl web sitesi tasarımı" | AI'nın ilk tasarımı (dar tek sütun, görselsiz) reddedildi. Geliştirici üç seçenek arasından "sıcak ve fotoğraflı" yönü, stok fotoğrafı ve renklerin AI tarafından önerilmesini seçti; site yeniden tasarlandı. |
| 15 | Değerlendirme kriterleri (hızlı form, canlı URL, açık kaynak, README, AI_LOG, teslim commit'i) | AI kriterleri tek tek karşılaştırıp eksikleri listeledi. Geliştirici Render + GitHub'ı ve iki formun birlikte kalmasını seçti. Hesapsız hızlı talep formu, kalıcı e2e test paketi, üretim imajı ve bu belge eklendi. |
| 16 | "Admin panelini de yapalım; login sonrası dashboard; üstte kartlar, 3/4 hizmet bazlı çizgi grafik + 1/4 son kayıtlar; kart: ikon+başlık, büyük değer, kıyas bilgisi, sağda büyük filigran ikon" | Dashboard API'si yazıldı; geliştirici grafik verisini (hızlı talep + başvuru), 7/30/90 gün seçimini ve tüm panel kapsamını seçti. |
| 17 | "Backend'de servis katmanı olacak, iş akışları ve okumalar burada; manager yalnızca queryset; serializer yalnızca doğrulama; Celery task servis dosyasında, sınıf dışında" | AI'nın o ana kadar yazdığı kod bu kurala uymuyordu (kayıt, başvuru ve hızlı talep oluşturma ile durum güncelleme serializer `create`/`validate` içinde, sorgular view'larda, durum kuralları modeldeydi). Tüm backend ayrı bir dalda servis katmanına taşındı; davranış testlerle bire bir korundu ve kuralı zorlayan mimari regresyon testi eklendi. Testin ihlali gerçekten yakaladığı, geçici olarak kuralı bozan bir serializer eklenerek doğrulandı. |

| 18 | "Tema koyu ve açık olsun, dil Türkçe ve İngilizce; seçim ülke bayraklarıyla, giriş sayfaları dahil her yerden" | Tercihler deposu, bayraklı seçici, iki dil dosyası ve koyu tema eklendi; hizmet adları backend'den istek diline göre dönüyor. |
| 19 | "Alt işleri daha düşük modelli worker'lara ver, raporlarını oku; tekrarlayan işleri betikle yap" → sonra "testleri her zaman worker'a bırak, sen geliştirmeye ve sonuçlara odaklan" | Test, ekran görüntüsü ve denetim işleri Sonnet/Haiku worker'larına verildi; ekran görüntüsü, test ve çeviri betikleri genişletildi. |
| 20 | "Dummy data için factory-boy kullan"; "factory'de servis değil doğrudan model kullan"; "Faker arayüzlerini kullan" | factory-boy fabrikaları yazıldı; kullanıcı fabrikası servis yerine `factory.django.Password` ile doğrudan modeli kullanacak şekilde düzeltildi; demo servisindeki elle yazılmış ad listeleri kaldırılıp Faker tanımlarına geçildi. |
| 21 | "Varsayılan şifreyi koda gömme, ayarlardan oku; testler dışarıdan değiştirebilsin" | `TEST_USER_PASSWORD` ve `DEMO_USER_PASSWORD` ayarları eklendi; sabit parola kullanan tüm testler bu ayara bağlandı. |
| 22 | "Çeviri için parler kullanıyorum; kullanıcı içerikleri için daha iyisi varsa kullan" ve "yalnızca sistemin sunduğu modeller çevrilsin, vatandaş tek dilde kayıt doldurur" | Hizmet türü ad/açıklaması django-parler'a taşındı; başvuru ve talepler çevrilmedi. |
| 23 | "Django ORM'den kaynaklı N+1'leri ayrı bir worker test etsin" | Tüm uç noktalar için kayıt sayısı artarken sorgu sayısını karşılaştıran testler yazıldı; N+1 bulunmadı. |
| 24 | "İstanbul geneli tematik harita: uzaktan tek sayı, yakınlaştıkça ilçe ve mahalle; sayıya basınca liste; toplam/hizmet seçimi; tek tonlu yoğunluk boyaması" | Geliştirici İstanbul'a özel ilçe/mahalle seçimini, hızlı forma da konum eklenmesini, MapLibre + OpenFreeMap'i ve önce parler'i seçti. Sınır verisi OpenStreetMap'ten üretildi; formlar ve harita buna göre yapıldı. |
| 25 | "Kullanılan her dış kaynağı iş sonunda belirt" | README'ye lisanslarıyla dış kaynaklar tablosu eklendi. |
| 26 | "Admin girişinde kullanıcı gibi davrandı, admin ekranları çıkmadı" | Doğru tespit: genel giriş sayfası yöneticiyi de başvuru sahibi sayfasına gönderiyordu ve sitede panele bağlantı yoktu. Yönlendirme ve üst bar bağlantısı eklendi. |
| 27 | "Bir worker tasarımdaki kaymalara, yapışık kenar ve kutulara, hatalı boşluklara baksın" | Tasarım denetimi 14 bulgu raporladı; düzeltildi ve ikinci bir worker ile doğrulandı. |

### AI önerisinin değiştirildiği / reddedildiği yerler

- **İlk görsel tasarım reddedildi** (madde 14). AI'nın tasarım planında başta "krem zemin + terracotta" vardı. AI bunu yapay zekâ çıktılarında sık görülen kalıp bir seçim olduğu için kendisi değiştirip "ıhlamur" yeşiline geçti; ancak bu sade tasarım da geliştirici tarafından beğenilmedi.
- **Sadece hesaplı başvuru akışı yetersiz bulundu** (madde 15). AI'nın kurduğu 5 adımlı, hesap gerektiren sihirbaz kriterlerdeki "isim, e-posta, hizmet, açıklama" formunu karşılamıyordu. Hesapsız hızlı form eklendi ve ana akış yapıldı.
- **Katman kuralına uyulmamıştı** (madde 17): AI iş mantığını serializer, model ve view'lara dağıtmıştı; geliştiricinin mimari kuralına göre servis katmanına taşındı.
- **Fabrikada servis katmanı kullanımı düzeltildi** (madde 20): AI kullanıcı fabrikasını servis katmanı üzerinden yazmıştı; geliştirici factory-boy'un doğrudan model oluşturduğunu söyledi, AI dokümantasyondan doğrulayıp değiştirdi. Demo verisinde Faker yerine elle yazılmış ad listeleri kullanılmıştı; Faker'a geçildi.
- **parler hakkında eksik ifade düzeltildi** (madde 22): AI "yeni dil migration gerektirmez" demişti; geliştirici parler'in kurulumda migration gerektirdiğini ve her dilin bir satır olduğunu hatırlattı. AI dokümantasyondan doğruladı.
- **README'deki yanlış iddia AI tarafından düzeltildi:** Harita altlığı kesilirse katmanların altlıksız çalışacağı yazılmıştı; kodla karşılaştırılınca doğru olmadığı görüldü ve metin düzeltildi.
- **Metin düzeltmesi:** AI'nın ana sayfaya kendisinin eklediği "Başvuru ücretsizdir" ifadesi, doğrulanmış bir bilgi olmadığı için yeniden tasarım sırasında kaldırıldı.

## 5. Bulunan ve düzeltilen gerçek hatalar

Aşağıdakiler oturumda testler veya kontroller sırasında **gerçekten** ortaya çıkan sorunlardır. Her biri commit geçmişinde görülebilir.

| Sorun | Nasıl bulundu | Düzeltme |
| --- | --- | --- |
| E-posta büyük harfle yazılınca giriş yapılamıyordu (kayıt küçük harfe çeviriyor, giriş tam eşleşme arıyordu) | Test klasörleri düzenlenirken kod incelemesi, sonra Docker'da elle denendi | Kullanıcı araması büyük/küçük harf duyarsız yapıldı; önce kırmızı, sonra yeşil olan regresyon testi eklendi |
| Türkçe I/İ/ı/i: PostgreSQL `LOWER('YILMAZ')` ≠ `LOWER('Yılmaz')`, mükerrer başvuru kısıtı kaçırıyordu | Mükerrer başvuru testleri başarısız oldu | Türkçe harf duyarlı `elder_name_key` alanı ve kısmi benzersizlik kısıtı eklendi |
| Refresh token'lar döndürülüyor ama eskileri kara listeye alınmıyordu; çıkışta oturum sunucuda kapanmıyordu | Senaryo testleri yazılırken fark edildi | Token kara listesi ve `/api/auth/logout/` eklendi; güvenlik testleri yazıldı |
| Sıfırdan kurulan yığında admin hesabı yoktu | Başlatma betiği planlanırken fark edildi | Ortam değişkenlerinden admin oluşturma eklendi |
| Windows'ta Python ile yazılan dosyalar CRLF oldu; `docker-entrypoint.sh` konteynerde çalışmadı | Backend konteyneri açılmadı (`no such file or directory`) | Dosyalar LF'ye çevrildi; sonraki betiklerde satır sonları kontrol edildi |
| Sihirbazın 4. ve 5. adımında başlık sırası h1'den h3'e atlıyordu | axe-core erişilebilirlik testi | Alt başlıklar h2 yapıldı |
| Sayfalar büyüyünce bazı yönlendirme testleri ara sıra başarısız oldu (tembel yükleme zamanlaması) | Test çalıştırması | Testler yönlendirmenin tamamlanmasını bekleyecek şekilde düzeltildi; 3 kez art arda çalıştırılarak kararlılık doğrulandı |
| Vite geliştirme sunucusu Vue eklentisini kaybetmiş durumda kaldı, ama sağlık kontrolü "sağlıklı" diyordu | Tarayıcı kontrolünde form görünmedi; konteyner günlükleri incelendi | Sağlık kontrolü `index.html` yerine derlenmiş bir Vue modülüne bakacak şekilde değiştirildi |
| Hata olunca odak ilk hatalı alana gidiyor ama yapışkan üst bar alanı örtüyordu | Ekran görüntüsü incelemesi; ardından konumlar ölçüldü | `scroll-margin-top` eklendi; alanın artık üst barın altında kalmadığı ölçülerek doğrulandı |
| Hızlı form saatte 5 istekle sınırlıyken e2e testleri 429 aldı | E2E çalıştırması | Hız sınırları yalnızca yerel compose ortamında gevşetildi; üretimde sıkı varsayılanlar kaldı |
| Bir birim testi ortam değişkenlerinden yalıtılmamıştı (compose'daki throttle ayarıyla başarısız oldu) | Tüm testlerin regresyon çalıştırması | Test, ilgili değişkeni geçici olarak kaldıracak şekilde yalıtıldı |
| Bir güvenlik testi boş formu gönderdiği için aslında hiçbir şeyi sınamıyordu | Testin kendisi gözden geçirildi | Test, formu doldurup gerçekten gönderecek şekilde düzeltildi |
| Windows test betiğinde sahte fonksiyon kaldırma komutu PowerShell'de çalışmıyordu | Windows betik testleri başarısız oldu | Doğru kaldırma sözdizimi kullanıldı; testler hem PowerShell 5.1 hem 7'de geçti |
| Üretim imajı yerelde HTTP üzerinden denenirken tarayıcı COOP uyarısı verdi | Üretim imajına karşı e2e | Uygulama hatası değil, HTTPS'te oluşmayan bir uyarı. Yalnızca bu uyarı, nedeni açıklanarak testte yok sayıldı |

**2. dönemde bulunanlar:**

| Sorun | Nasıl bulundu | Düzeltme |
| --- | --- | --- |
| Genel giriş sayfası yöneticiyi başvuru sahibi sayfasına gönderiyordu; sitede panele bağlantı yoktu | Geliştirici fark etti | Yönetici panele yönlendirildi, üst bara "Yönetim paneli" bağlantısı eklendi; regresyon testi yazıldı |
| parler önbelleği ve Django dil ara katmanı testler arasında eski dili taşıyordu (Türkçe istek İngilizce ad döndürdü) | Backend testleri | Önbellek kapatıldı (çeviriler zaten önceden yükleniyor); fabrikalar varsayılan dile sabitlendi |
| parler'e geçişte migration'lar çalışmadı; geri alma `NOT NULL` hatası verdi | Migration'lar uygulanırken ve geri alınırken | İlk migration'a parler katmanı eklendi; kaldırma adımına boş varsayılan eklendi; geri alma ve ileri alma ayrıca denendi |
| Admin detay adreslerinde `\d+` düzeni tekleşmişti; detay sayfaları "bulunamadı"ya düşüyordu | Testler | Düzen düzeltildi; regresyon testi eklendi |
| Hızlı talep servisi mahalleyi almıyordu; serializer'da proje kuralına aykırı sorgu vardı; taslaktan açılan özet mahalle adını göstermiyordu | Test worker'ı | Üçü de düzeltildi |
| Harita çekmecesi her açılışta aynı isteği iki kez gönderiyordu | Test worker'ı | Tek izleyiciye indirildi |
| Bildirim bileşenine verilen sınıf sayfanın sağ yarısını örtüyordu; halka grafik sıfır yükseklikte çizilmiyordu; mobilde çekmeceler ekranı doldurmuyordu | Ekran görüntüsü incelemesi | Sınıf kaldırıldı, grafik kapsayıcısına boyut verildi, çekmece genişliği düzeltildi |
| MapLibre 6'nın varsayılan dışa aktarımı yok; worker dosyası Vite'ta yüklenmiyordu | Tarayıcı konsolu | Adlandırılmış içe aktarım ve `?worker&url` ile ayrı derlenen worker kullanıldı; üretim derlemesi ayrıca doğrulandı |
| Koyu temada kapanış bandı ve turuncu düğmeler okunmuyordu; oturum açıkken üst bar iki satıra bölünüyordu | Tasarım denetimi worker'ı | Tema değişkenleri eklendi; üst bar her genişlikte tek satıra indirildi ve kenar payları ölçülerek eşitlendi |
| Ön yüz test paketi büyüyünce tam paralel çalışmada ara sıra zaman aşımı oldu | Art arda test çalıştırmaları | Vitest paralelliği sınırlandı ve test süresi artırıldı |

Ayrıca birkaç test yazım hatası (yanlış seçici, sahte komut düzeneği) testler çalıştırılınca ortaya çıktı ve düzeltildi. Bunlar uygulama hatası olmadığından tabloya alınmadı.

## 6. Doğrulama: neyi, nasıl sınadım

1. **Her commit öncesi tüm testler** Docker konteynerlerinde, PostgreSQL üzerinde çalıştırıldı (regresyon).
   - 1.0.0'da backend 169, frontend 170 testti. 1.1.0'da backend **301**, frontend **444** test; ön yüze `regression` türü eklendi.
   - 2. dönemde testleri worker'lar yazdı ve çalıştırdı; ana model raporları okudu, "hepsi geçti" raporlarını dosyaları inceleyerek ya da kendi ekran görüntüsü kontrolüyle doğruladı. Haiku tabanlı bir görsel kontrol worker'ı bir kez gerçek bir sorunu (mobilde dar çekmece) kaçırdı; bu yüzden önemli görüntüler ana model tarafından da incelendi.
2. **Uçtan uca (Playwright), 18 test:** 9 senaryo × telefon ve masaüstü, gerçek backend ve veritabanına karşı.
   - Hızlı formun "Gönderiliyor…" durumu.
   - Başarı mesajındaki kayıt numarasının admin API'sinde aynı kayıtla eşleşmesi (kalıcı saklama).
   - 500 hatasında başarı mesajının hiç çıkmaması.
   - İstemci atlatıldığında sunucu doğrulaması.
   - Kayıt → 5 adımlı başvuru → mükerrer başvurunun reddi.
   - Yatay taşma ve konsol hatası kontrolü.
   - Bu paket hem geliştirme yığınına hem **üretim Docker imajına** karşı çalıştırıldı.
3. **Görsel kontrol:** Her ekran 390, 820 ve 1366 px genişlikte ekran görüntüsüyle incelendi. Görüntüler üzerinden bulunan sorunlar düzeltildi:
   - Logo bir yüze benziyordu.
   - Kapanış kartını dikey fotoğraf uzatıyordu.
   - Tablette telefon numarası iki satıra bölünüyordu.
   - Yapışkan üst bar hatalı alanı örtüyordu.
4. **Üretim imajı:** `DEBUG=False` ile ayrı bir veritabanında çalıştırıldı.
   - Sayfa adresleri, API, görseller, Swagger ve olmayan API adresleri (404) tek tek denendi.
   - `manage.py check --deploy` uyarıları incelendi; her biri ya düzeltildi ya da nedeniyle README'ye yazıldı.
5. **Başlatma betikleri:**
   - Unix betikleri shellcheck'ten geçti ve Ubuntu konteynerinde 9 senaryoda denendi.
   - Windows betiği PowerShell 5.1 ve 7'de 7 senaryoda denendi; ayrıca bu makinede gerçekten çalıştırılıp durduruldu.
   - Gerçek bir macOS veya Linux makinesinde **denenmedi**.
6. **Çeviriler:** Her değişiklikte `makemessages` ile katalog yenilendi; boş, bulanık (fuzzy) ve eskimiş girdi kalmadığı denetlendi.

## 7. Bilinen eksikler

- Harita altlığı OpenFreeMap'in ücretsiz hizmetinden gelir; erişilemezse harita açılmaz (sıralama ve listeler çalışır).
- Konum sorulmaya başlanmadan önceki kayıtlar haritada sayılmaz.
- Kullanıcı yönetimi salt okunurdur.
- Hızlı talep gelince ekibe veya kişiye **e-posta gönderilmiyor**; talepler kaydediliyor ve admin API'sinden görülüyor.
- Başvurular internetten düzenlenemiyor veya iptal edilemiyor (SSS'de "bizi arayın" deniyor).
- İletişim telefonu ve çalışma saatleri yer tutucudur.
- Render ücretsiz katmanında uygulama boşta uyur (ilk istek yaklaşık 30 sn); ücretsiz PostgreSQL 30 gün sonra silinir.
- Tarayıcı token'ları `localStorage`'da tutuluyor. Access token kısa ömürlü, refresh token'lar döndürülüp kara listeye alınıyor; daha sıkı bir model için httpOnly çerez tercih edilebilir.

## 8. Veri

Testlerde, demo verisinde (`care_create_demo_data`, ayrılmış `demo.yanimda.example` alan adı, Faker ile üretilen adlar) ve denemelerde yalnızca **kurgusal veriler** kullanıldı (`example.com` e-postaları, "Deneme Kişi", "Kurgusal Yaşlı" gibi adlar, `0555 000 00 00` gibi numaralar). Gerçek kişi verisi kullanılmadı.
