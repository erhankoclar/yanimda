import { createPinia } from 'pinia'
import { createApp } from 'vue'

import { installAdminUiGuard } from './admin/installAdminUiGuard'
import App from './App.vue'
import { i18n } from './i18n'
import { createAppRouter } from './router'
import { usePreferencesStore } from './stores/preferences'

const pinia = createPinia()
const app = createApp(App)
const router = createAppRouter({ pinia })

app.use(pinia)
app.use(i18n)
// Kayıtlı dil ve tema ilk çizimden önce uygulanır.
usePreferencesStore(pinia)
// PrimeVue yalnızca admin route'larına girildiğinde yüklenir; guard router'dan önce kurulmalı.
installAdminUiGuard(router, app)
app.use(router)
app.mount('#app')
