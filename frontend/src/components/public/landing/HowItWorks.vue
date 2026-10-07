<script setup>
const STEPS = [
  { title: 'İhtiyacınızı anlatın', text: 'Hangi hizmet, kimin için, ne zaman ve nerede: beş kısa adımda.' },
  { title: 'Sizi arayalım', text: 'Ekibimiz başvurunuzu inceler ve ayrıntıları konuşmak için verdiğiniz numaradan sizi arar.' },
  { title: 'Destek başlasın', text: 'Uygun kişi atanır. Başvurunuzun durumunu her zaman “Başvurularım” sayfasından görebilirsiniz.' },
]
</script>

<template>
  <section class="how-it-works" aria-labelledby="how-title">
    <h2 id="how-title">Nasıl işler?</h2>
    <ol class="how-it-works__list">
      <li v-for="step in STEPS" :key="step.title" class="how-it-works__step">
        <h3>{{ step.title }}</h3>
        <p>{{ step.text }}</p>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.how-it-works {
  margin-top: var(--space-7);
}

.how-it-works__list {
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: step;
}

.how-it-works__step {
  position: relative;
  padding: 0 0 var(--space-5) 3.5rem;
  counter-increment: step;
}

.how-it-works__step::before {
  content: counter(step);
  position: absolute;
  left: 0;
  top: -0.1rem;
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: var(--color-ink);
  color: var(--color-paper);
  font-weight: 800;
}

/* Adımları birbirine bağlayan dikey çizgi sürecin sırasını gösterir. */
.how-it-works__step:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 1.2rem;
  top: 2.6rem;
  bottom: 0.2rem;
  width: 2px;
  background: var(--color-line);
}

.how-it-works__step h3 {
  margin-bottom: var(--space-1);
  font-size: var(--text-lg);
}

.how-it-works__step p {
  margin: 0;
  color: var(--color-ink-soft);
}
</style>
