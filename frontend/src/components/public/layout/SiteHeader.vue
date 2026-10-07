<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import PreferenceControls from '@/components/common/PreferenceControls.vue'

import BrandMark from './BrandMark.vue'

defineProps({
  authenticated: { type: Boolean, required: true },
})

const emit = defineEmits({
  /** Kullanıcı çıkış düğmesine bastığında. */
  logout: null,
})

const { t } = useI18n()
const route = useRoute()
const menuOpen = ref(false)

// Başka sayfaya geçildiğinde mobil menü kapanır.
watch(() => route.fullPath, () => {
  menuOpen.value = false
})

// Bölüm bağlantıları; etiketler etkin dile göre çözülür.
const sections = computed(() => [
  { hash: '#hizmetler', label: t('nav.sections.services') },
  { hash: '#nasil-isler', label: t('nav.sections.how') },
  { hash: '#sss', label: t('nav.sections.faq') },
])
</script>

<template>
  <header class="site-header">
    <div class="container site-header__bar">
      <RouterLink :to="{ name: 'landing' }" class="site-header__brand" :aria-label="t('nav.homeLabel')">
        <BrandMark />
      </RouterLink>

      <div class="site-header__tools">
        <PreferenceControls />
        <button
          type="button"
          class="site-header__toggle"
          :aria-expanded="menuOpen ? 'true' : 'false'"
          aria-controls="site-menu"
          @click="menuOpen = !menuOpen"
        >
          <span class="site-header__toggle-lines" aria-hidden="true" />
          {{ menuOpen ? t('nav.close') : t('nav.menu') }}
        </button>
      </div>

      <div id="site-menu" class="site-header__menu" :class="{ 'is-open': menuOpen }">
        <nav class="site-header__sections" :aria-label="t('nav.sectionsLabel')">
          <RouterLink v-for="section in sections" :key="section.hash" :to="{ name: 'landing', hash: section.hash }">
            {{ section.label }}
          </RouterLink>
        </nav>
        <nav class="site-header__account" :aria-label="t('nav.accountLabel')">
          <template v-if="authenticated">
            <RouterLink :to="{ name: 'request-list' }">{{ t('common.myRequests') }}</RouterLink>
            <button type="button" class="site-header__logout" @click="emit('logout')">{{ t('nav.logout') }}</button>
          </template>
          <RouterLink v-else :to="{ name: 'login' }">{{ t('nav.login') }}</RouterLink>
          <RouterLink class="site-header__cta" :to="{ name: 'landing', hash: '#talep-formu' }">{{ t('common.leaveRequest') }}</RouterLink>
        </nav>
      </div>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 20;
  border-bottom: 1px solid var(--color-line);
  background: var(--color-header-bg);
  backdrop-filter: blur(8px);
}

.site-header__bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  min-height: 4.5rem;
}

.site-header__brand {
  color: var(--color-ink);
  text-decoration: none;
}

.site-header__tools {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.site-header__toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 2.75rem;
  padding: 0 var(--space-4);
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-ink);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.site-header__toggle-lines,
.site-header__toggle-lines::before,
.site-header__toggle-lines::after {
  display: block;
  width: 1.1rem;
  height: 2px;
  border-radius: 2px;
  background: currentColor;
}

.site-header__toggle-lines {
  position: relative;
}

.site-header__toggle-lines::before,
.site-header__toggle-lines::after {
  content: '';
  position: absolute;
  left: 0;
}

.site-header__toggle-lines::before {
  top: -6px;
}

.site-header__toggle-lines::after {
  top: 6px;
}

.site-header__menu {
  display: none;
  flex-basis: 100%;
  padding-bottom: var(--space-4);
}

.site-header__menu.is-open {
  display: grid;
  gap: var(--space-4);
}

.site-header__sections,
.site-header__account {
  display: grid;
  gap: var(--space-1);
}

.site-header__menu a {
  display: flex;
  align-items: center;
  min-height: 2.75rem;
  color: var(--color-ink);
  font-weight: 700;
  text-decoration: none;
}

.site-header__menu a:hover {
  color: var(--color-primary);
}

.site-header__logout {
  justify-self: start;
  min-height: 2.75rem;
  padding: 0;
  border: 0;
  background: none;
  color: var(--color-ink);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.site-header__menu .site-header__cta {
  justify-content: center;
  margin-top: var(--space-2);
  padding: 0 var(--space-5);
  border-radius: 999px;
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.site-header__menu .site-header__cta:hover {
  background: var(--color-primary-dark);
  color: var(--color-on-primary);
}

@media (min-width: 60rem) {
  .site-header__toggle {
    display: none;
  }

  .site-header__tools {
    order: 3;
  }

  .site-header__menu,
  .site-header__menu.is-open {
    display: flex;
    flex: 1;
    flex-basis: auto;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-6);
    padding: 0 0 0 var(--space-7);
  }

  .site-header__sections,
  .site-header__account {
    display: flex;
    align-items: center;
    gap: var(--space-5);
  }

  .site-header__menu .site-header__cta {
    margin-top: 0;
  }
}
</style>
