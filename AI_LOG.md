# AI_LOG — Yanımda

Bu belge, projenin yapay zekâ ile nasıl üretildiğini, hangi kararların kime ait olduğunu ve sonucun nasıl doğrulandığını kayıt altına alır. Bilgiler oturumun kendisinden ve commit geçmişinden (`git log`) alınmıştır; tahmin veya uydurma içermez.

## 1. Süre

- İlk commit: 2026-10-07 17:09 — teslim belgeleri yazılırken son commit: 2026-10-07 20:32.
- Toplam çalışma: **yaklaşık 3,5 saat**, tek oturumda. Süre commit zaman damgalarından hesaplanmıştır; PRD'nin yazılması bu sürenin dışındadır.

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

Hazır bir proje şablonu (boilerplate) kullanılmadı. Django iskeleti `django-admin startproject/startapp` komutlarıyla oluşturuldu, Vite projesi elle kuruldu. Kodun geri kalanı bu oturumda yazıldı.

## 3. Görev dağılımı

| Kim | Sorumluluk |
| --- | --- |
| **Geliştirici (ürün sahibi)** | PRD'yi yazdı; teknoloji ve kapsam kararlarını verdi; ara sonuçları inceleyip yönlendirdi (aşağıdaki liste); tasarım yönünü, görsel kaynağını ve yayın platformunu seçti; GitHub deposunu oluşturdu. |
| **AI (Claude Code)** | Planı çıkardı, tüm kodu ve testleri yazdı, testleri ve tarayıcı kontrollerini çalıştırdı, hataları buldu ve düzeltti, commit'leri attı, belgeleri yazdı. Belirsiz noktalarda seçenek sunup kararı geliştiriciye bıraktı. |

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

### AI önerisinin değiştirildiği / reddedildiği yerler

- **İlk görsel tasarım reddedildi** (madde 14). AI'nın tasarım planında başta "krem zemin + terracotta" vardı. AI bunu yapay zekâ çıktılarında sık görülen kalıp bir seçim olduğu için kendisi değiştirip "ıhlamur" yeşiline geçti; ancak bu sade tasarım da geliştirici tarafından beğenilmedi.
- **Sadece hesaplı başvuru akışı yetersiz bulundu** (madde 15). AI'nın kurduğu 5 adımlı, hesap gerektiren sihirbaz kriterlerdeki "isim, e-posta, hizmet, açıklama" formunu karşılamıyordu. Hesapsız hızlı form eklendi ve ana akış yapıldı.
- **Katman kuralına uyulmamıştı** (madde 17): AI iş mantığını serializer, model ve view'lara dağıtmıştı; geliştiricinin mimari kuralına göre servis katmanına taşındı.
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

Ayrıca birkaç test yazım hatası (yanlış seçici, sahte komut düzeneği) testler çalıştırılınca ortaya çıktı ve düzeltildi. Bunlar uygulama hatası olmadığından tabloya alınmadı.

## 6. Doğrulama: neyi, nasıl sınadım

1. **Her commit öncesi tüm testler** Docker konteynerlerinde, PostgreSQL üzerinde çalıştırıldı (regresyon).
   - Backend: 169 test; `unit`, `integration`, `security`, `regression`, `contract`, `performance`, `scenario` türlerinde.
   - Frontend: 170 test (Vitest); `unit`, `component`, `integration`, `security`, `accessibility` türlerinde.
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

- **Admin panel ekranları yapılmadı.** Admin API'leri (talepler, durum güncelleme, istatistik, kullanıcılar, hızlı talepler) hazır ve test edildi; Vue tarafındaki admin sayfaları yalnızca başlık içeriyor. Değerlendirme kriterlerinde yer almadığı için öncelik son kullanıcı tarafına verildi.
- Hızlı talep gelince ekibe veya kişiye **e-posta gönderilmiyor**; talepler kaydediliyor ve admin API'sinden görülüyor.
- Başvurular internetten düzenlenemiyor veya iptal edilemiyor (SSS'de "bizi arayın" deniyor).
- İletişim telefonu ve çalışma saatleri yer tutucudur.
- Render ücretsiz katmanında uygulama boşta uyur (ilk istek yaklaşık 30 sn); ücretsiz PostgreSQL 30 gün sonra silinir.
- Tarayıcı token'ları `localStorage`'da tutuluyor. Access token kısa ömürlü, refresh token'lar döndürülüp kara listeye alınıyor; daha sıkı bir model için httpOnly çerez tercih edilebilir.

## 8. Veri

Testlerde ve denemelerde yalnızca **kurgusal veriler** kullanıldı (`example.com` e-postaları, "Deneme Kişi", "Kurgusal Yaşlı" gibi adlar, `0555 000 00 00` gibi numaralar). Gerçek kişi verisi kullanılmadı.
