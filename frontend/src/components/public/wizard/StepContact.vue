<script setup>
import { useI18n } from 'vue-i18n'

import BaseInput from '../BaseInput.vue'

const { t } = useI18n()

defineProps({
  form: { type: Object, required: true },
  errors: { type: Object, required: true },
})
</script>

<template>
  <div>
    <BaseInput
      v-model="form.contact_phone"
      :label="t('wizard.contact.phone')"
      type="tel"
      inputmode="tel"
      autocomplete="tel"
      :hint="t('wizard.contact.phoneHint')"
      required
      :error="errors.contact_phone"
    />
    <h2 class="step-contact__subtitle">{{ t('wizard.contact.alternateTitle') }}</h2>
    <p class="step-contact__note">{{ t('wizard.contact.alternateNote') }}</p>
    <BaseInput
      v-model="form.alternate_contact_name"
      :label="t('wizard.contact.alternateName')"
      autocomplete="off"
      :error="errors.alternate_contact_name"
    />
    <BaseInput
      v-model="form.alternate_contact_phone"
      :label="t('wizard.contact.alternatePhone')"
      type="tel"
      inputmode="tel"
      autocomplete="off"
      :error="errors.alternate_contact_phone"
    />
  </div>
</template>

<style scoped>
.step-contact__subtitle {
  margin-top: var(--space-6);
  font-size: var(--text-lg);
}

.step-contact__note {
  color: var(--color-ink-soft);
}
</style>
