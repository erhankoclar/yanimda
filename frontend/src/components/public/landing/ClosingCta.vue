<template>
  <section class="closing" aria-labelledby="closing-title">
    <div class="container">
      <div class="closing__card">
        <div class="closing__text">
          <h2 id="closing-title">Hazır olduğunuzda buradayız</h2>
          <p>Başvurunuzu yarıda bırakmanız gerekirse sorun değil; yazdıklarınız bu tarayıcı sekmesinde saklanır.</p>
          <RouterLink class="closing__cta" :to="{ name: 'request-new' }">Başvuruya başla</RouterLink>
        </div>
        <div class="closing__media">
          <img
            class="closing__photo"
            src="/images/holding-hands.webp"
            alt="Genç bir elin yaşlı bir eli şefkatle tuttuğu yakın çekim"
            width="900"
            height="1350"
            loading="lazy"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.closing {
  padding: var(--space-7) 0;
}

.closing__card {
  display: grid;
  overflow: hidden;
  border-radius: 2rem;
  background: var(--color-primary);
  color: #fff;
}

.closing__text {
  padding: var(--space-6) var(--space-5);
}

.closing h2 {
  color: #fff;
  font-size: clamp(2rem, 5vw, 2.75rem);
}

.closing p {
  color: #dcebe7;
  font-size: var(--text-lg);
}

.closing__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: var(--tap-size);
  margin-top: var(--space-3);
  padding: var(--space-3) var(--space-6);
  border-radius: 999px;
  background: var(--color-accent);
  color: var(--color-ink);
  font-weight: 700;
  text-decoration: none;
}

.closing__cta:hover {
  background: #f6b475;
}

/* Fotoğraf kartın yüksekliğine uyar; dikey görsel kartı uzatmaz. */
.closing__media {
  position: relative;
  min-height: 16rem;
}

.closing__photo {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (min-width: 60rem) {
  .closing__card {
    grid-template-columns: 1.3fr 1fr;
    align-items: stretch;
  }

  .closing__text {
    align-self: center;
    padding: var(--space-7);
  }

  .closing__media {
    min-height: 22rem;
  }
}
</style>
