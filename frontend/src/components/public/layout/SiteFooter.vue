<script setup>
import { useI18n } from 'vue-i18n'

import BrandMark from './BrandMark.vue'

const { t } = useI18n()
const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="container site-footer__grid">
      <div class="site-footer__about">
        <BrandMark />
        <p>{{ t('footer.about') }}</p>
      </div>
      <nav :aria-label="t('footer.navLabel')">
        <h2 class="site-footer__title">{{ t('footer.siteTitle') }}</h2>
        <ul>
          <li><RouterLink :to="{ name: 'landing', hash: '#hizmetler' }">{{ t('nav.sections.services') }}</RouterLink></li>
          <li><RouterLink :to="{ name: 'landing', hash: '#nasil-isler' }">{{ t('nav.sections.how') }}</RouterLink></li>
          <li><RouterLink :to="{ name: 'landing', hash: '#sss' }">{{ t('nav.sections.faq') }}</RouterLink></li>
          <li><RouterLink :to="{ name: 'request-list' }">{{ t('common.myRequests') }}</RouterLink></li>
        </ul>
      </nav>
      <div>
        <h2 class="site-footer__title">{{ t('footer.contactTitle') }}</h2>
        <p class="site-footer__phone"><a href="tel:+908500000000">0850 000 00 00</a></p>
        <p>{{ t('footer.hours') }}</p>
      </div>
    </div>
    <div class="container site-footer__bottom">
      <p>{{ t('footer.copyright', { year }) }}</p>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  margin-top: var(--space-7);
  padding-top: var(--space-7);
  background: var(--color-deep);
  color: #dfe9e5;
}

.site-footer a {
  color: #fff;
}

.site-footer__grid {
  display: grid;
  gap: var(--space-6);
  padding-bottom: var(--space-6);
}

.site-footer__about :deep(.brand-mark__text) {
  color: #fff;
}

.site-footer__about p {
  margin-top: var(--space-3);
}

.site-footer__title {
  margin-bottom: var(--space-3);
  color: #fff;
  font-size: var(--text-base);
}

.site-footer ul {
  display: grid;
  gap: var(--space-2);
  margin: 0;
  padding: 0;
  list-style: none;
}

.site-footer__phone {
  margin-bottom: var(--space-1);
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
}

.site-footer__phone a {
  text-decoration: none;
  white-space: nowrap;
}

.site-footer__bottom {
  padding-bottom: var(--space-5);
  font-size: var(--text-sm);
}

/* Ayırıcı çizgi kapsayıcının iç boşluğuna değil metnin genişliğine uyar. */
.site-footer__bottom p {
  margin: 0;
  padding-top: var(--space-4);
  border-top: 1px solid rgb(255 255 255 / 0.15);
}

@media (min-width: 48rem) {
  .site-footer__grid {
    grid-template-columns: 2fr 1fr 1fr;
  }
}
</style>
