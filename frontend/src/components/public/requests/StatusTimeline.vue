<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const FLOW = [
  { value: 'new', title: 'Başvurunuz alındı', text: 'Bilgileriniz ekibimize ulaştı.' },
  { value: 'reviewing', title: 'İnceleniyor', text: 'Ekibimiz başvurunuzu inceliyor ve sizi arayacak.' },
  { value: 'assigned', title: 'Kişi atandı', text: 'Yakınınıza destek olacak kişi belirlendi.' },
  { value: 'completed', title: 'Tamamlandı', text: 'Hizmet verildi.' },
]

// İptal edilen başvurularda akış yerine tek bir açıklama gösterilir.
const isCancelled = computed(() => props.status === 'cancelled')
// Akıştaki geçerli adımın sırası.
const currentIndex = computed(() => FLOW.findIndex((step) => step.value === props.status))
</script>

<template>
  <p v-if="isCancelled" class="status-timeline__cancelled">
    Bu başvuru iptal edildi. İhtiyacınız sürüyorsa aynı hizmete yeniden başvurabilirsiniz.
  </p>
  <ol v-else class="status-timeline">
    <li
      v-for="(step, index) in FLOW"
      :key="step.value"
      class="status-timeline__step"
      :class="{ 'is-done': index < currentIndex, 'is-current': index === currentIndex }"
      :aria-current="index === currentIndex ? 'step' : undefined"
    >
      <span class="status-timeline__title">{{ step.title }}</span>
      <span v-if="index <= currentIndex" class="status-timeline__text">{{ step.text }}</span>
    </li>
  </ol>
</template>

<style scoped>
.status-timeline {
  margin: 0;
  padding: 0;
  list-style: none;
}

.status-timeline__step {
  position: relative;
  padding: 0 0 var(--space-4) 2.5rem;
  color: var(--color-ink-soft);
}

.status-timeline__step::before {
  content: '';
  position: absolute;
  left: 0.25rem;
  top: 0.2rem;
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid var(--color-line);
  border-radius: 50%;
  background: var(--color-surface);
}

.status-timeline__step:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 0.82rem;
  top: 1.6rem;
  bottom: 0.2rem;
  width: 2px;
  background: var(--color-line);
}

.status-timeline__step.is-done::before {
  border-color: var(--color-primary);
  background: var(--color-primary);
}

.status-timeline__step.is-done::after {
  background: var(--color-primary);
}

.status-timeline__step.is-current {
  color: var(--color-ink);
}

.status-timeline__step.is-current::before {
  border: 5px solid var(--color-accent);
  background: var(--color-ink);
}

.status-timeline__title {
  display: block;
  font-weight: 700;
}

.status-timeline__text {
  display: block;
  font-size: var(--text-sm);
}

.status-timeline__cancelled {
  padding: var(--space-4);
  border-radius: var(--radius-control);
  background: var(--color-line);
}
</style>
