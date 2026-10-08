<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <section aria-labelledby="not-found-title">
    <h1 id="not-found-title">{{ t('notFound.title') }}</h1>
    <p>{{ t('notFound.text') }}</p>
    <p>
      <RouterLink :to="{ name: 'landing' }">{{ t('notFound.home') }}</RouterLink>
      {{ t('notFound.or') }}
      <RouterLink :to="{ name: 'request-list' }">{{ t('notFound.requests') }}</RouterLink>.
    </p>
  </section>
</template>
