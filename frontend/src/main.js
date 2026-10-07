import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { createAppRouter } from './router'

const pinia = createPinia()

createApp(App).use(pinia).use(createAppRouter({ pinia })).mount('#app')
