<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Cevaplar sistemin gerçek kurallarına dayanır; kural değişirse çeviri kataloğu da güncellenmelidir.
const QUESTION_KEYS = ['requirements', 'afterwards', 'again', 'change', 'privacy', 'self']

// Etkin dildeki soru ve cevaplar; dil değişince yeniden hesaplanır.
const questions = computed(() => QUESTION_KEYS.map((key) => ({
  key,
  question: t(`landing.faq.items.${key}.question`),
  answer: t(`landing.faq.items.${key}.answer`),
})))
</script>

<template>
  <section id="sss" class="faq" aria-labelledby="faq-title">
    <div class="container faq__grid">
      <div>
        <h2 id="faq-title">{{ t('landing.faq.title') }}</h2>
        <p class="faq__intro">{{ t('landing.faq.intro') }} <a href="tel:+908500000000">0850 000 00 00</a></p>
      </div>
      <div class="faq__list">
        <details v-for="item in questions" :key="item.key" class="faq__item">
          <summary>{{ item.question }}</summary>
          <p>{{ item.answer }}</p>
        </details>
      </div>
    </div>
  </section>
</template>

<style scoped>
.faq {
  padding: var(--space-7) 0;
  background: var(--color-peach);
}

.faq h2 {
  font-size: clamp(2rem, 5vw, 2.75rem);
}

.faq__intro {
  color: var(--color-ink-soft);
}

.faq__grid {
  display: grid;
  gap: var(--space-5);
}

.faq__list {
  display: grid;
  gap: var(--space-3);
}

.faq__item {
  border-radius: 1rem;
  background: var(--color-surface);
}

.faq__item summary {
  position: relative;
  padding: var(--space-4) 3.5rem var(--space-4) var(--space-5);
  font-weight: 700;
  list-style: none;
  cursor: pointer;
}

.faq__item summary::-webkit-details-marker {
  display: none;
}

/* Açılıp kapandığını gösteren artı/eksi işareti. */
.faq__item summary::after {
  content: '+';
  position: absolute;
  right: var(--space-5);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-primary);
  font-family: var(--font-display);
  font-size: 1.75rem;
  line-height: 1;
}

.faq__item[open] summary::after {
  content: '−';
}

.faq__item p {
  margin: 0;
  padding: 0 var(--space-5) var(--space-5);
  color: var(--color-ink-soft);
  max-width: none;
}

@media (min-width: 60rem) {
  .faq__grid {
    grid-template-columns: 1fr 2fr;
    gap: var(--space-7);
  }
}
</style>
