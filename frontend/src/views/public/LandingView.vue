<script setup>
import HowItWorks from '@/components/public/landing/HowItWorks.vue'
import ServiceOverview from '@/components/public/landing/ServiceOverview.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="landing container">
    <section class="landing__hero" aria-labelledby="landing-title">
      <h1 id="landing-title">Annenizin, babanızın yanında olalım.</h1>
      <p class="landing__lead">
        Evde bakım, refakat, hastane eşliği ya da günlük işler. Yakınınızın neye ihtiyacı olduğunu
        birkaç adımda anlatın; ekibimiz sizi arayıp birlikte planlasın.
      </p>
      <div class="landing__actions">
        <RouterLink class="landing__cta" :to="{ name: 'request-new' }">Başvuruya başla</RouterLink>
        <RouterLink v-if="auth.isAuthenticated" class="landing__secondary" :to="{ name: 'request-list' }">
          Başvurularımı gör
        </RouterLink>
      </div>
      <p class="landing__trust">Başvuru ücretsizdir. Bilgileriniz yalnızca hizmeti planlamak için kullanılır.</p>
    </section>

    <ServiceOverview />
    <HowItWorks />

    <section class="landing__closing" aria-labelledby="closing-title">
      <h2 id="closing-title">Hazır olduğunuzda buradayız</h2>
      <p>Başvurunuzu yarıda bırakmanız gerekirse sorun değil; dilediğiniz zaman yeniden başlayabilirsiniz.</p>
      <RouterLink class="landing__cta" :to="{ name: 'request-new' }">Başvuruya başla</RouterLink>
    </section>
  </div>
</template>

<style scoped>
.landing__hero {
  padding-top: var(--space-5);
}

.landing__hero h1 {
  font-size: clamp(2.25rem, 8vw, 3.25rem);
  line-height: 1.1;
  max-width: 12em;
}

.landing__lead {
  font-size: var(--text-lg);
}

.landing__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-4);
  margin: var(--space-5) 0 var(--space-4);
}

.landing__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: var(--tap-size);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-control);
  background: var(--color-primary);
  color: #fff;
  font-weight: 700;
  text-decoration: none;
}

.landing__cta:hover {
  background: var(--color-primary-dark);
}

.landing__secondary {
  font-weight: 700;
}

.landing__trust {
  color: var(--color-ink-soft);
  font-size: var(--text-sm);
}

.landing__closing {
  margin-top: var(--space-7);
  padding: var(--space-6) var(--space-5);
  border-radius: var(--radius-card);
  background: var(--color-primary-tint);
}

@media (max-width: 30rem) {
  .landing__cta {
    width: 100%;
  }
}
</style>
