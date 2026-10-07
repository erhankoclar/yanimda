<script setup>
import BaseInput from '../BaseInput.vue'

defineProps({
  form: { type: Object, required: true },
  errors: { type: Object, required: true },
})
</script>

<template>
  <div>
    <BaseInput
      v-model="form.contact_phone"
      label="Size hangi numaradan ulaşalım?"
      type="tel"
      inputmode="tel"
      autocomplete="tel"
      hint="Örnek: 0555 123 45 67"
      required
      :error="errors.contact_phone"
    />
    <h2 class="step-contact__subtitle">Size ulaşamazsak kimi arayalım?</h2>
    <p class="step-contact__note">Bu bölüm isteğe bağlıdır. Doldurursanız ad ve telefonu birlikte yazın.</p>
    <BaseInput
      v-model="form.alternate_contact_name"
      label="İkinci kişinin adı"
      autocomplete="off"
      :error="errors.alternate_contact_name"
    />
    <BaseInput
      v-model="form.alternate_contact_phone"
      label="İkinci kişinin telefonu"
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
