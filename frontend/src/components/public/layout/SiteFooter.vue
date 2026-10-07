<script setup>
import BrandMark from './BrandMark.vue'

const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="container site-footer__grid">
      <div class="site-footer__about">
        <BrandMark />
        <p>Yaşlı yakınlarınız için evde bakım, refakat, hastane eşliği ve günlük işlerde destek başvurusu.</p>
      </div>
      <nav aria-label="Alt bilgi">
        <h2 class="site-footer__title">Site</h2>
        <ul>
          <li><RouterLink :to="{ name: 'landing', hash: '#hizmetler' }">Hizmetler</RouterLink></li>
          <li><RouterLink :to="{ name: 'landing', hash: '#nasil-isler' }">Nasıl işler?</RouterLink></li>
          <li><RouterLink :to="{ name: 'landing', hash: '#sss' }">Sık sorulanlar</RouterLink></li>
          <li><RouterLink :to="{ name: 'request-list' }">Başvurularım</RouterLink></li>
        </ul>
      </nav>
      <div>
        <h2 class="site-footer__title">Bize ulaşın</h2>
        <p class="site-footer__phone"><a href="tel:+908500000000">0850 000 00 00</a></p>
        <p>Hafta içi 09:00–18:00</p>
      </div>
    </div>
    <div class="container site-footer__bottom">
      <p>© {{ year }} Yanımda</p>
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
}

.site-footer__bottom {
  padding-top: var(--space-4);
  padding-bottom: var(--space-5);
  border-top: 1px solid rgb(255 255 255 / 0.15);
  font-size: var(--text-sm);
}

.site-footer__bottom p {
  margin: 0;
}

@media (min-width: 48rem) {
  .site-footer__grid {
    grid-template-columns: 2fr 1fr 1fr;
  }
}
</style>
