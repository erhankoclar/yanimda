import { createPinia } from 'pinia'
import { createApp } from 'vue'

import { installAdminUiGuard } from './admin/installAdminUiGuard'
import App from './App.vue'
import { createAppRouter } from './router'

const pinia = createPinia()
const app = createApp(App)
const router = createAppRouter({ pinia })

app.use(pinia)
// PrimeVue yalnızca admin route'larına girildiğinde yüklenir; guard router'dan önce kurulmalı.
installAdminUiGuard(router, app)
app.use(router)
app.mount('#app')
