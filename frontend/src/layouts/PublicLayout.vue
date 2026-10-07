<script setup>
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useRequestWizardStore } from '@/stores/requestWizard'

import '@/styles/public.css'

const auth = useAuthStore()
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
    <a class="skip-link" href="#main-content">İçeriğe geç</a>
    <header class="site-header">
      <RouterLink :to="{ name: 'landing' }" class="site-header__brand">Yanımda</RouterLink>
      <nav class="site-header__nav" aria-label="Hesap">
        <template v-if="auth.isAuthenticated">
          <RouterLink :to="{ name: 'request-list' }">Başvurularım</RouterLink>
          <button type="button" class="site-header__logout" @click="logout">Çıkış yap</button>
        </template>
        <RouterLink v-else :to="{ name: 'login' }">Giriş yap</RouterLink>
      </nav>
    </header>
    <main id="main-content" class="site-main" tabindex="-1">
      <RouterView />
    </main>
    <footer class="site-footer">
      <p>Sorunuz mu var? Bizi arayın: <a href="tel:+908500000000">0850 000 00 00</a></p>
    </footer>
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
  z-index: 10;
}

.skip-link:focus {
  top: var(--space-4);
}

.site-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-4);
}

.site-header__brand {
  font-size: var(--text-lg);
  font-weight: 800;
  color: var(--color-ink);
  text-decoration: none;
}

.site-header__nav {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-size: var(--text-sm);
}

.site-header__nav a {
  font-weight: 700;
}

.site-header__logout {
  min-height: 2.75rem;
  padding: 0 var(--space-3);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-control);
  background: var(--color-surface);
  color: var(--color-ink);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.site-main {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-5) var(--space-4) var(--space-7);
}

.site-main:focus {
  outline: none;
}

.site-footer {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-5) var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-line);
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}
</style>
