<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  /** Adım başlıkları, sırasıyla. */
  steps: { type: Array, required: true },
  /** Etkin adımın sıfırdan başlayan sırası. */
  current: { type: Number, required: true },
})

// Ekranda ve ekran okuyucuda okunacak "Adım 2 / 5" metni.
const summary = computed(() => t('wizard.progress.summary', { current: props.current + 1, total: props.steps.length }))
// İlerleme çubuğunun doluluk oranı.
const percent = computed(() => Math.round(((props.current + 1) / props.steps.length) * 100))
</script>

<template>
  <nav class="wizard-progress" :aria-label="t('wizard.progress.label')">
    <p class="wizard-progress__summary">
      <span>{{ summary }}</span>
      <strong>{{ steps[current] }}</strong>
    </p>
    <div class="wizard-progress__bar" aria-hidden="true">
      <span class="wizard-progress__fill" :style="{ width: `${percent}%` }" />
    </div>
    <ol class="wizard-progress__steps">
      <li
        v-for="(step, index) in steps"
        :key="step"
        :aria-current="index === current ? 'step' : undefined"
        :class="{ 'is-done': index < current, 'is-current': index === current }"
      >
        {{ step }}<span v-if="index < current" class="visually-hidden"> {{ t('wizard.progress.done') }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.wizard-progress {
  margin-bottom: var(--space-6);
}

.wizard-progress__summary {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-3);
  margin: 0 0 var(--space-3);
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}

.wizard-progress__summary strong {
  color: var(--color-ink);
}

.wizard-progress__bar {
  height: 0.5rem;
  border-radius: 999px;
  background: var(--color-line);
  overflow: hidden;
}

.wizard-progress__fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--color-primary);
  transition: width 250ms ease;
}

/* Adım listesi yalnızca ekran okuyucular içindir; görsel olarak çubuk ve özet yeterlidir. */
.wizard-progress__steps {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
}
</style>
