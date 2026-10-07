<script setup>
import ClosingCta from '@/components/public/landing/ClosingCta.vue'
import FaqSection from '@/components/public/landing/FaqSection.vue'
import HowItWorks from '@/components/public/landing/HowItWorks.vue'
import LandingHero from '@/components/public/landing/LandingHero.vue'
import ServiceOverview from '@/components/public/landing/ServiceOverview.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="landing">
    <LandingHero :authenticated="auth.isAuthenticated" />
    <ServiceOverview />
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
  color: #fff;
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
