<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const STEP_KEYS = ['describe', 'call', 'start']

// Etkin dildeki adımlar; dil değişince yeniden hesaplanır.
const steps = computed(() => STEP_KEYS.map((key) => ({
  key,
  title: t(`landing.how.steps.${key}.title`),
  text: t(`landing.how.steps.${key}.text`),
})))
</script>

<template>
  <section id="nasil-isler" class="how-it-works" aria-labelledby="how-title">
    <div class="container how-it-works__grid">
      <img
        class="how-it-works__photo"
        src="/images/escort-walk.webp"
        :alt="t('landing.how.photoAlt')"
        width="900"
        height="1350"
        loading="lazy"
      />
      <div>
        <h2 id="how-title">{{ t('landing.how.title') }}</h2>
        <p class="how-it-works__intro">{{ t('landing.how.intro') }}</p>
        <ol class="how-it-works__list">
          <li v-for="step in steps" :key="step.key" class="how-it-works__step">
            <h3>{{ step.title }}</h3>
            <p>{{ step.text }}</p>
          </li>
        </ol>
        <RouterLink class="landing__cta" :to="{ name: 'request-new' }">{{ t('common.startApplication') }}</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.how-it-works {
  padding: var(--space-7) 0;
}

.how-it-works__grid {
  display: grid;
  gap: var(--space-6);
  align-items: center;
}

.how-it-works h2 {
  font-size: clamp(2rem, 5vw, 2.75rem);
}

.how-it-works__photo {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  object-position: center 30%;
  border-radius: 2rem;
}

.how-it-works__intro {
  color: var(--color-ink-soft);
  font-size: var(--text-lg);
}

.how-it-works__list {
  margin: var(--space-5) 0 var(--space-6);
  padding: 0;
  list-style: none;
  counter-reset: step;
}

.how-it-works__step {
  position: relative;
  padding: 0 0 var(--space-5) 4rem;
  counter-increment: step;
}

.how-it-works__step::before {
  content: counter(step);
  position: absolute;
  left: 0;
  top: -0.2rem;
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 50%;
  background: var(--color-accent);
  color: var(--color-on-accent);
  font-family: var(--font-display);
  font-weight: 800;
}

/* Adımları birbirine bağlayan dikey çizgi sürecin sırasını gösterir. */
.how-it-works__step:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 1.33rem;
  top: 2.8rem;
  bottom: 0.3rem;
  width: 2px;
  background: var(--color-line);
}

.how-it-works__step h3 {
  margin-bottom: var(--space-1);
  font-size: var(--text-lg);
}

.how-it-works__step p {
  margin: 0;
  color: var(--color-ink-soft);
}

@media (min-width: 60rem) {
  .how-it-works__grid {
    grid-template-columns: 0.85fr 1fr;
    gap: 5rem;
  }

  .how-it-works__photo {
    max-height: 34rem;
    aspect-ratio: 4 / 5;
  }
}
</style>
