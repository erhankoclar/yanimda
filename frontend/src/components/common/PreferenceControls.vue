<script setup>
import { useI18n } from 'vue-i18n'

import { usePreferencesStore } from '@/stores/preferences'

import FlagIcon from './FlagIcon.vue'

const preferences = usePreferencesStore()
const { t } = useI18n()

const LANGUAGES = [
  { code: 'tr', labelKey: 'preferences.turkish' },
  { code: 'en', labelKey: 'preferences.english' },
]
</script>

<template>
  <div class="preference-controls">
    <div class="preference-controls__languages" role="group" :aria-label="t('preferences.language')">
      <button
        v-for="language in LANGUAGES"
        :key="language.code"
        type="button"
        class="preference-controls__flag"
        :class="{ 'is-active': preferences.locale === language.code }"
        :aria-pressed="preferences.locale === language.code ? 'true' : 'false'"
        :aria-label="t('preferences.switchTo', { language: t(language.labelKey) })"
        :title="t(language.labelKey)"
        :lang="language.code"
        @click="preferences.setLocale(language.code)"
      >
        <FlagIcon :code="language.code" />
      </button>
    </div>
    <button
      type="button"
      class="preference-controls__theme"
      :aria-label="preferences.isDark ? t('preferences.switchToLight') : t('preferences.switchToDark')"
      :title="preferences.isDark ? t('preferences.lightTheme') : t('preferences.darkTheme')"
      @click="preferences.toggleTheme()"
    >
      <svg v-if="preferences.isDark" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <circle cx="12" cy="12" r="4.5" />
        <path d="M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8 6 18M18 6l1.8-1.8" />
      </svg>
      <svg v-else viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.preference-controls {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.preference-controls__languages {
  display: inline-flex;
  gap: 0.25rem;
  padding: 0.2rem;
  border: 1px solid var(--pref-line, rgb(0 0 0 / 0.12));
  border-radius: 999px;
}

.preference-controls__flag,
.preference-controls__theme {
  display: inline-grid;
  place-items: center;
  min-width: 2.75rem;
  min-height: 2.75rem;
  padding: 0;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.preference-controls__flag {
  min-width: 2.5rem;
  min-height: 2.25rem;
  opacity: 0.55;
}

.preference-controls__flag.is-active {
  opacity: 1;
  background: var(--pref-active, rgb(0 0 0 / 0.06));
}

.preference-controls__flag:hover {
  opacity: 1;
}

.preference-controls__theme {
  border: 1px solid var(--pref-line, rgb(0 0 0 / 0.12));
}

.preference-controls__theme svg {
  width: 1.25rem;
  height: 1.25rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
