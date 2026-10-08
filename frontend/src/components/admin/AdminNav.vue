<script setup>
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

defineEmits({
  /** Bir bağlantıya tıklandı; mobil menü kapanabilir. */
  navigate: null,
})

const { t } = useI18n()
const route = useRoute()

// Kenar çubuğu ve mobil menüde aynı sırayla gösterilen bölümler.
// `routes`: bölümün etkin sayılacağı sayfalar (detay sayfaları kardeş route olduğu için ayrıca yazılır).
const ITEMS = [
  { name: 'admin-dashboard', icon: 'pi pi-th-large', labelKey: 'admin.nav.dashboard', routes: ['admin-dashboard'] },
  { name: 'admin-inquiries', icon: 'pi pi-inbox', labelKey: 'admin.nav.inquiries', routes: ['admin-inquiries'] },
  { name: 'admin-requests', icon: 'pi pi-file-edit', labelKey: 'admin.nav.requests', routes: ['admin-requests', 'admin-request-detail'] },
  { name: 'admin-users', icon: 'pi pi-users', labelKey: 'admin.nav.users', routes: ['admin-users', 'admin-user-detail'] },
]

/**
 * Bölümün şu anki sayfayı kapsayıp kapsamadığını söyler.
 *
 * @param {{ routes: string[] }} item Menü öğesi.
 * @returns {boolean} Etkinse true.
 */
function isActive(item) {
  return item.routes.includes(route.name)
}
</script>

<template>
  <nav class="admin-nav" :aria-label="t('admin.nav.label')">
    <ul>
      <li v-for="item in ITEMS" :key="item.name">
        <RouterLink
          :to="{ name: item.name }"
          class="admin-nav__link"
          :class="{ 'is-active': isActive(item) }"
          :aria-current="isActive(item) ? 'page' : undefined"
          @click="$emit('navigate')"
        >
          <i :class="item.icon" aria-hidden="true" />
          <span>{{ t(item.labelKey) }}</span>
        </RouterLink>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.admin-nav ul {
  display: grid;
  gap: 0.25rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.admin-nav__link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 2.75rem;
  padding: 0 0.85rem;
  border-radius: 0.6rem;
  color: var(--admin-ink-soft);
  font-weight: 700;
  text-decoration: none;
}

.admin-nav__link:hover {
  background: var(--admin-bg);
  color: var(--admin-ink);
}

/* Alt sayfalar (ör. başvuru detayı) da kendi bölümünü etkin gösterir. */
.admin-nav__link.is-active {
  background: var(--admin-primary-tint);
  color: var(--admin-primary);
}

.admin-nav__link:focus-visible {
  outline: 2px solid var(--admin-primary);
  outline-offset: 2px;
}

.admin-nav__link i {
  font-size: 1.05rem;
}
</style>
