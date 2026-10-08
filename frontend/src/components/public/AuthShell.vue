<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  /** Sayfa başlığının kimliği; bölüm aria-labelledby ile buna bağlanır. */
  titleId: { type: String, required: true },
})
</script>

<template>
  <section class="auth-shell" :aria-labelledby="titleId">
    <div class="auth-shell__form">
      <div class="auth-shell__inner">
        <slot />
      </div>
    </div>
    <aside class="auth-shell__visual" aria-hidden="true">
      <img src="/images/care-at-home.webp" alt="" width="1200" height="800" />
      <div class="auth-shell__quote">
        <p class="auth-shell__quote-title">{{ t('auth.shell.title') }}</p>
        <p>{{ t('auth.shell.text') }}</p>
      </div>
    </aside>
  </section>
</template>

<style scoped>
.auth-shell {
  display: grid;
  min-height: calc(100vh - 4.5rem);
  background: var(--color-mist);
}

.auth-shell__form {
  display: grid;
  align-items: center;
  padding: var(--space-6) var(--space-4) var(--space-7);
}

.auth-shell__inner {
  width: 100%;
  max-width: 30rem;
  margin: 0 auto;
  padding: var(--space-6) var(--space-5);
  border-radius: 1.5rem;
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
}

.auth-shell__visual {
  display: none;
}

@media (min-width: 60rem) {
  .auth-shell {
    grid-template-columns: 1fr 1fr;
  }

  .auth-shell__inner {
    padding: var(--space-7) var(--space-6);
  }

  .auth-shell__visual {
    position: relative;
    display: block;
    overflow: hidden;
  }

  .auth-shell__visual img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .auth-shell__quote {
    position: absolute;
    left: var(--space-6);
    right: var(--space-6);
    bottom: var(--space-6);
    padding: var(--space-5) var(--space-6);
    border-radius: 1.5rem;
    background: rgb(20 60 54 / 0.88);
    color: #dcebe7;
  }

  .auth-shell__quote p {
    margin: 0;
  }

  .auth-shell__quote .auth-shell__quote-title {
    margin-bottom: var(--space-2);
    color: #fff;
    font-family: var(--font-display);
    font-size: var(--text-xl);
    font-weight: 700;
    line-height: 1.2;
  }
}
</style>
