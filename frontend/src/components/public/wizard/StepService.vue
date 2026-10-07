<script setup>
import ServiceCard from '../ServiceCard.vue'

const selected = defineModel({ type: Number, default: null })

defineProps({
  services: { type: Array, required: true },
  /** Hizmet listesinin yükleme durumu: loading, ready veya error. */
  status: { type: String, required: true },
  error: { type: String, default: '' },
})

const emit = defineEmits({
  /** Kullanıcı yüklemeyi tekrar denemek istediğinde. */
  retry: null,
})
</script>

<template>
  <fieldset class="wizard-fieldset">
    <legend class="visually-hidden">Hizmet seçin</legend>
    <p v-if="status === 'loading' || status === 'idle'" role="status">Hizmetler yükleniyor…</p>
    <div v-else-if="status === 'error'" role="alert">
      <p>Hizmetler yüklenemedi. İnternet bağlantınızı kontrol edip tekrar deneyin.</p>
      <button type="button" class="link-button" @click="emit('retry')">Tekrar dene</button>
    </div>
    <div v-else class="step-service__cards">
      <ServiceCard v-for="service in services" :key="service.id" v-model="selected" :service="service" name="service" />
    </div>
    <p v-if="error" class="field__error" role="alert">{{ error }}</p>
  </fieldset>
</template>

<style scoped>
.step-service__cards {
  display: grid;
  gap: var(--space-3);
}
</style>
