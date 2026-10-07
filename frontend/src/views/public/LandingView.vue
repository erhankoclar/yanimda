<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import ClosingCta from '@/components/public/landing/ClosingCta.vue'
import FaqSection from '@/components/public/landing/FaqSection.vue'
import HowItWorks from '@/components/public/landing/HowItWorks.vue'
import InquiryForm from '@/components/public/landing/InquiryForm.vue'
import LandingHero from '@/components/public/landing/LandingHero.vue'
import ServiceOverview from '@/components/public/landing/ServiceOverview.vue'
import { useServices } from '@/composables/useServices'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
// Hizmetler bir kez yüklenir; hem kartlarda hem talep formunda kullanılır.
const { services, status, load } = useServices()

// Hizmet kartından gelindiyse formda seçili olacak hizmet.
const selectedService = computed(() => Number(route.query.service) || null)

onMounted(load)
</script>

<template>
  <div class="landing">
    <LandingHero :authenticated="auth.isAuthenticated" />
    <ServiceOverview :services="services" :status="status" @retry="load" />
    <InquiryForm :services="services" :initial-service="selectedService" />
    <HowItWorks />
    <FaqSection />
    <ClosingCta />
  </div>
</template>

<style scoped>
/* Ana sayfadaki birincil çağrı düğmeleri (hero ve "Nasıl işler?" bölümü). */
.landing :deep(.landing__cta) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: var(--tap-size);
  padding: var(--space-3) var(--space-6);
  border-radius: 999px;
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-weight: 700;
  text-decoration: none;
}

.landing :deep(.landing__cta:hover) {
  background: var(--color-primary-dark);
}

@media (max-width: 30rem) {
  .landing :deep(.landing__cta) {
    width: 100%;
  }
}
</style>
