<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  authenticated: { type: Boolean, default: false },
})

const { t } = useI18n()

const PROMISE_KEYS = ['services', 'call', 'track']
</script>

<template>
  <section class="hero" aria-labelledby="landing-title">
    <div class="container hero__grid">
      <div class="hero__text">
        <h1 id="landing-title">{{ t('landing.hero.title') }}</h1>
        <p class="hero__lead">
          {{ t('landing.hero.lead') }}
        </p>
        <div class="hero__actions">
          <RouterLink class="landing__cta" :to="{ name: 'landing', hash: '#talep-formu' }">{{ t('common.leaveRequest') }}</RouterLink>
          <RouterLink v-if="authenticated" class="landing__secondary" :to="{ name: 'request-list' }">
            {{ t('landing.hero.viewRequests') }}
          </RouterLink>
          <RouterLink v-else class="landing__secondary" :to="{ name: 'request-new' }">
            {{ t('landing.hero.detailed') }}
          </RouterLink>
        </div>
        <ul class="hero__promises">
          <li v-for="key in PROMISE_KEYS" :key="key">{{ t(`landing.hero.promises.${key}`) }}</li>
        </ul>
      </div>

      <div class="hero__visual">
        <img
          class="hero__photo"
          src="/images/hero-mother-daughter.webp"
          :alt="t('landing.hero.photoAlt')"
          width="1400"
          height="934"
          fetchpriority="high"
        />
        <div class="hero__status" aria-hidden="true">
          <span class="hero__status-dot" />
          <span>
            <strong>{{ t('landing.hero.statusTitle') }}</strong>
            <span class="hero__status-text">{{ t('landing.hero.statusText') }}</span>
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  padding: var(--space-6) 0 var(--space-7);
  background: linear-gradient(180deg, var(--color-peach) 0%, var(--color-paper) 100%);
}

.hero__grid {
  display: grid;
  gap: var(--space-6);
  align-items: center;
}

.hero h1 {
  font-size: clamp(2.5rem, 7vw, 4rem);
  line-height: 1.02;
  font-weight: 800;
  max-width: 11em;
}

.hero__lead {
  font-size: var(--text-lg);
  max-width: 28em;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-4) var(--space-5);
  margin: var(--space-5) 0;
}

.hero__secondary,
.landing__secondary {
  font-weight: 700;
}

.hero__promises {
  display: grid;
  gap: var(--space-2);
  margin: 0;
  padding: 0;
  list-style: none;
  color: var(--color-ink-soft);
}

.hero__promises li {
  position: relative;
  padding-left: 2rem;
}

.hero__promises li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.25em;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  background: var(--color-primary-tint)
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231f5f55' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 12.5 4 4 8-9'/%3E%3C/svg%3E")
    center / 0.8rem no-repeat;
}

.hero__visual {
  position: relative;
}

.hero__photo {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: 2rem;
  box-shadow: var(--shadow-soft);
}

.hero__status {
  position: absolute;
  left: var(--space-4);
  bottom: calc(var(--space-5) * -1);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5) var(--space-3) var(--space-4);
  border-radius: 1rem;
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
  font-size: var(--text-sm);
}

.hero__status strong {
  display: block;
}

.hero__status-text {
  color: var(--color-ink-soft);
}

.hero__status-dot {
  flex: none;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: var(--color-primary)
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 12.5 4 4 8-9'/%3E%3C/svg%3E")
    center / 1.1rem no-repeat;
}

@media (min-width: 60rem) {
  .hero {
    padding: var(--space-7) 0 5rem;
  }

  .hero__grid {
    grid-template-columns: 1.05fr 1fr;
    gap: var(--space-7);
  }

  .hero__status {
    left: calc(var(--space-6) * -1);
    bottom: var(--space-6);
  }
}
</style>
