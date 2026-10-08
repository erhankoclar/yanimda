<script setup>
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

import SiteFooter from '@/components/public/layout/SiteFooter.vue'
import SiteHeader from '@/components/public/layout/SiteHeader.vue'
import { useAuthStore } from '@/stores/auth'
import { useRequestWizardStore } from '@/stores/requestWizard'

import '@/styles/public.css'

const { t } = useI18n()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const wizard = useRequestWizardStore()

/** Oturumu kapatır, kişisel bilgi içeren başvuru taslağını siler ve ana sayfaya döner. */
async function logout() {
  wizard.reset()
  await auth.logout()
  await router.push({ name: 'landing' })
}
</script>

<template>
  <div class="public-layout" data-layout="public">
    <a class="skip-link" href="#main-content">{{ t('common.skipToContent') }}</a>
    <SiteHeader :authenticated="auth.isAuthenticated" :is-admin="auth.isAdmin" @logout="logout" />
    <main
      id="main-content"
      class="site-main"
      :class="route.meta.fullWidth ? 'site-main--full' : 'site-main--page'"
      tabindex="-1"
    >
      <RouterView v-if="route.meta.fullWidth" />
      <div v-else class="site-main__page">
        <RouterView />
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<style scoped>
.skip-link {
  position: absolute;
  left: var(--space-4);
  top: -4rem;
  padding: var(--space-3) var(--space-4);
  background: var(--color-ink);
  color: var(--color-surface);
  border-radius: var(--radius-control);
  z-index: 30;
}

.skip-link:focus {
  top: var(--space-4);
}

.site-main:focus {
  outline: none;
}

.site-main--page {
  background: var(--color-mist);
}

.site-main__page {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-6) var(--space-4) var(--space-7);
}

.public-layout :deep(.site-footer) {
  margin-top: 0;
}
</style>
