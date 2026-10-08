<script setup>
import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

import AdminBrand from '@/components/admin/AdminBrand.vue'
import AdminNav from '@/components/admin/AdminNav.vue'
import PreferenceControls from '@/components/common/PreferenceControls.vue'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const menuOpen = ref(false)

// Üst bardaki sayfa başlığı route tanımındaki anahtardan gelir; sayfanın tek h1'idir.
const pageTitle = computed(() => (route.meta.titleKey ? t(route.meta.titleKey) : t('admin.brand')))

/** Oturumu kapatır ve admin girişine döner. */
async function logout() {
  await auth.logout()
  await router.replace({ name: 'admin-login' })
}
</script>

<template>
  <div class="admin-shell admin-layout" data-layout="admin">
    <aside class="admin-layout__sidebar">
      <RouterLink :to="{ name: 'admin-dashboard' }" class="admin-layout__brand">
        <AdminBrand />
      </RouterLink>
      <AdminNav />
      <a href="/" class="admin-layout__site-link" target="_blank" rel="noopener">
        <i class="pi pi-external-link" aria-hidden="true" />
        {{ t('admin.layout.openSite') }}
      </a>
    </aside>

    <Drawer v-model:visible="menuOpen" position="left" class="admin-shell admin-layout__drawer" :pt="{ root: { 'aria-label': t('admin.nav.label') } }">
      <template #header>
        <AdminBrand />
      </template>
      <AdminNav @navigate="menuOpen = false" />
      <a href="/" class="admin-layout__site-link" target="_blank" rel="noopener">
        <i class="pi pi-external-link" aria-hidden="true" />
        {{ t('admin.layout.openSite') }}
      </a>
    </Drawer>

    <div class="admin-layout__main">
      <header class="admin-layout__topbar">
        <Button
          class="admin-layout__menu-toggle"
          icon="pi pi-bars"
          text
          rounded
          :aria-label="t('admin.layout.openMenu')"
          :aria-expanded="menuOpen ? 'true' : 'false'"
          @click="menuOpen = true"
        />
        <h1 class="admin-layout__title">{{ pageTitle }}</h1>
        <div class="admin-layout__tools">
          <PreferenceControls />
          <span class="admin-layout__user" :title="t('admin.layout.signedInAs', { name: auth.displayName })">
            <i class="pi pi-user" aria-hidden="true" />
            <span class="admin-layout__user-name">{{ auth.displayName }}</span>
          </span>
          <Button
            class="admin-layout__logout"
            icon="pi pi-sign-out"
            :label="t('admin.layout.logout')"
            severity="secondary"
            text
            @click="logout"
          />
        </div>
      </header>
      <main class="admin-layout__content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 1fr;
}

.admin-layout__sidebar {
  display: none;
}

.admin-layout__main {
  min-width: 0;
}

.admin-layout__topbar {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 4rem;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--admin-line);
  background: var(--admin-surface);
}

.admin-layout__title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  font-size: 1.2rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.admin-layout__tools {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.admin-layout__user {
  display: none;
  align-items: center;
  gap: 0.4rem;
  max-width: 14rem;
  color: var(--admin-ink-soft);
  font-weight: 700;
}

.admin-layout__user-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Dar ekranda çıkış yalnızca simgeyle gösterilir; etiketi ekran okuyucuya kalır. */
.admin-layout__logout :deep(.p-button-label) {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.admin-layout__content {
  padding: 1rem;
}

.admin-layout__brand {
  display: block;
  padding: 0.25rem 0.5rem 1.25rem;
  color: var(--admin-ink);
  text-decoration: none;
}

.admin-layout__site-link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: auto;
  padding: 0.75rem 0.85rem;
  color: var(--admin-ink-soft);
  font-weight: 700;
  text-decoration: none;
}

.admin-layout__site-link:hover {
  color: var(--admin-primary);
}

/* Dar ekranda tercih denetimleri ve kullanıcı alanı sığsın diye başlık küçülür. */
@media (max-width: 30rem) {
  .admin-layout__title {
    font-size: 1.05rem;
  }
}

@media (min-width: 48rem) {
  .admin-layout__user {
    display: inline-flex;
  }

  .admin-layout__logout :deep(.p-button-label) {
    position: static;
    width: auto;
    height: auto;
    overflow: visible;
    clip-path: none;
  }

  .admin-layout__content {
    padding: 1.5rem;
  }
}

@media (min-width: 64rem) {
  .admin-layout {
    grid-template-columns: var(--admin-sidebar-width) minmax(0, 1fr);
  }

  .admin-layout__sidebar {
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 1.25rem 0.85rem;
    border-right: 1px solid var(--admin-line);
    background: var(--admin-surface);
  }

  .admin-layout__menu-toggle {
    display: none;
  }

  .admin-layout__topbar {
    padding: 0.5rem 1.5rem;
  }

  .admin-layout__content {
    padding: 1.75rem;
  }
}
</style>

<style>
/* Drawer body'ye taşındığı için token'lar .admin-shell sınıfıyla ona da verilir. */
.admin-layout__drawer.admin-shell {
  min-height: 0;
}

.admin-layout__drawer .p-drawer-content {
  display: flex;
  flex-direction: column;
}
</style>
