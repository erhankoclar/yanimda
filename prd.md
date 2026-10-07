# Frontend Teknoloji Ayrımı

Projede iki farklı arayüz bulunacaktır:

1. Son kullanıcı arayüzü
2. Admin panel arayüzü

Her iki taraf da Vue 3 ile geliştirilecektir.

Ancak PrimeVue yalnızca admin panel arayüzünde kullanılacaktır.

---

# Son Kullanıcı Arayüzü

Teknoloji:

- Vue 3
- Vue Router
- Axios
- Standart CSS / scoped CSS
- Gerekirse küçük ve bağımsız ikon kütüphanesi

PrimeVue kullanılmayacaktır.

Son kullanıcı tarafında amaç hazır bir component framework görünümü vermek değil, ürüne özel sade ve sıcak bir kullanıcı deneyimi oluşturmaktır.

Arayüz:

- mobile-first,
- responsive,
- sade,
- büyük ve anlaşılır aksiyonlara sahip,
- adım adım yönlendiren,
- yaşlı yakını adına başvuru yapan kişiyi yormayan

bir yapıda olacaktır.

Tüm inputlar aynı anda gösterilmeyecektir.

Başvuru wizard şeklinde ilerleyecektir.

---

# Son Kullanıcı İçin Yasak

Son kullanıcı frontendinde:

- PrimeVue
- DataTable
- admin panel görünümlü bileşenler
- yoğun dashboard yapıları
- teknik yönetim paneli hissi veren hazır component tasarımları

kullanılmayacaktır.

---

# Son Kullanıcı Hizmet Kartları

Hizmetler özel Vue componentleri ile yapılacaktır.

Örnek:

ServiceCard.vue

Her kart:

- büyük ikon,
- hizmet adı,
- kısa açıklama,
- hover state,
- focus state,
- selected state

içerecektir.

Kartlar büyük seçim butonu / jumbo card mantığında çalışacaktır.

---

# Son Kullanıcı Form Bileşenleri

Örnek:

BaseInput.vue
BaseSelect.vue
BaseTextarea.vue
BaseCheckbox.vue
PrimaryButton.vue
WizardProgress.vue

Bu componentler proje içinde basit şekilde geliştirilecektir.

Amaç component library oluşturmak değildir.

Yalnızca tekrar kullanılan alanlar component haline getirilmelidir.

---

# Admin Panel

Teknoloji:

- Vue 3
- Vue Router
- Axios
- PrimeVue

PrimeVue yalnızca admin tarafında kullanılacaktır.

Admin panel:

- sidebar,
- topbar,
- dashboard,
- DataTable,
- filtreler,
- dialog,
- badge,
- select,
- input,
- pagination

gibi yönetim bileşenlerinde PrimeVue kullanabilir.

---

# Admin Route Yapısı

/admin/login
/admin/dashboard
/admin/users
/admin/users/:id
/admin/requests
/admin/requests/:id

---

# Admin Layout

Admin tarafı ayrı layout kullanacaktır.

Örnek:

AdminLayout.vue

İçerik:

- sidebar
- topbar
- breadcrumb opsiyonel
- content area

Son kullanıcı layout'u ile admin layout'u karıştırılmamalıdır.

---

# Frontend Klasör Yapısı

frontend/
│
├── src/
│ ├── api/
│ │ ├── auth.js
│ │ ├── requests.js
│ │ └── admin.js
│ │
│ ├── components/
│ │ ├── public/
│ │ │ ├── ServiceCard.vue
│ │ │ ├── WizardProgress.vue
│ │ │ ├── BaseInput.vue
│ │ │ ├── BaseSelect.vue
│ │ │ └── PrimaryButton.vue
│ │ │
│ │ └── admin/
│ │ └── PrimeVue tabanlı componentler
│ │
│ ├── layouts/
│ │ ├── PublicLayout.vue
│ │ └── AdminLayout.vue
│ │
│ ├── views/
│ │ ├── public/
│ │ │ ├── LandingView.vue
│ │ │ ├── LoginView.vue
│ │ │ ├── RegisterView.vue
│ │ │ ├── NewRequestView.vue
│ │ │ ├── RequestListView.vue
│ │ │ └── RequestDetailView.vue
│ │ │
│ │ └── admin/
│ │ ├── AdminLoginView.vue
│ │ ├── DashboardView.vue
│ │ ├── UsersView.vue
│ │ ├── UserDetailView.vue
│ │ ├── RequestsView.vue
│ │ └── RequestDetailView.vue
│ │
│ ├── router/
│ ├── stores/
│ └── styles/
│
└── package.json

---

# Tasarım Ayrımı

Son kullanıcı:

duygusal olarak sıcak,
sade,
ferah,
büyük yazılar,
büyük aksiyon alanları,
az seçenek,
wizard akışı.

Admin:

daha yoğun bilgi,
tablo,
filtre,
istatistik,
durum yönetimi,
operasyon odaklı.

İki arayüz görsel ve kullanım amacı olarak birbirinden net biçimde ayrılmalıdır.
