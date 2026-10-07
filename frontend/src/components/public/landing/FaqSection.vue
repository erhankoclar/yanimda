<script setup>
// Cevaplar sistemin gerçek kurallarına dayanır; kural değişirse burası da güncellenmelidir.
const QUESTIONS = [
  {
    question: 'Başvuru için neler gerekiyor?',
    answer: 'Bir hesap, yakınınızın adı ve yaşı, hizmetin verileceği adres ve size ulaşabileceğimiz bir telefon numarası yeterli.',
  },
  {
    question: 'Başvurudan sonra ne olacak?',
    answer: 'Ekibimiz başvurunuzu inceler ve verdiğiniz numaradan sizi arar. Başvurunuzun hangi aşamada olduğunu “Başvurularım” sayfasından görebilirsiniz.',
  },
  {
    question: 'Aynı hizmete ikinci kez başvurabilir miyim?',
    answer: 'Aynı yakınınız için aynı hizmette açık bir başvurunuz varken yenisi açılamaz. Başvuru tamamlandığında ya da iptal edildiğinde yeniden başvurabilirsiniz. Anneniz ve babanız için ayrı ayrı başvurmanız mümkündür.',
  },
  {
    question: 'Başvurumu değiştirebilir veya iptal edebilir miyim?',
    answer: 'Gönderilen başvuru internetten değiştirilemez. Değişiklik ya da iptal için bizi arayın; ekibimiz başvurunuzu güncellesin.',
  },
  {
    question: 'Bilgilerim nasıl kullanılıyor?',
    answer: 'Yazdığınız bilgiler yalnızca hizmeti planlamak ve sizinle iletişim kurmak için kullanılır. Başvuruyu gönderirken verdiğiniz onay, tarihiyle birlikte kaydedilir.',
  },
  {
    question: 'Kendim için başvurabilir miyim?',
    answer: 'Evet. Başvuruda yakınlık olarak “Kendim” seçeneğini işaretlemeniz yeterli.',
  },
]
</script>

<template>
  <section id="sss" class="faq" aria-labelledby="faq-title">
    <div class="container faq__grid">
      <div>
        <h2 id="faq-title">Sık sorulanlar</h2>
        <p class="faq__intro">Aradığınız cevabı bulamazsanız bizi arayın: <a href="tel:+908500000000">0850 000 00 00</a></p>
      </div>
      <div class="faq__list">
        <details v-for="item in QUESTIONS" :key="item.question" class="faq__item">
          <summary>{{ item.question }}</summary>
          <p>{{ item.answer }}</p>
        </details>
      </div>
    </div>
  </section>
</template>

<style scoped>
.faq {
  padding: var(--space-7) 0;
  background: var(--color-peach);
}

.faq h2 {
  font-size: clamp(2rem, 5vw, 2.75rem);
}

.faq__intro {
  color: var(--color-ink-soft);
}

.faq__grid {
  display: grid;
  gap: var(--space-5);
}

.faq__list {
  display: grid;
  gap: var(--space-3);
}

.faq__item {
  border-radius: 1rem;
  background: var(--color-surface);
}

.faq__item summary {
  position: relative;
  padding: var(--space-4) 3.5rem var(--space-4) var(--space-5);
  font-weight: 700;
  list-style: none;
  cursor: pointer;
}

.faq__item summary::-webkit-details-marker {
  display: none;
}

/* Açılıp kapandığını gösteren artı/eksi işareti. */
.faq__item summary::after {
  content: '+';
  position: absolute;
  right: var(--space-5);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-primary);
  font-family: var(--font-display);
  font-size: 1.75rem;
  line-height: 1;
}

.faq__item[open] summary::after {
  content: '−';
}

.faq__item p {
  margin: 0;
  padding: 0 var(--space-5) var(--space-5);
  color: var(--color-ink-soft);
  max-width: none;
}

@media (min-width: 60rem) {
  .faq__grid {
    grid-template-columns: 1fr 2fr;
    gap: var(--space-7);
  }
}
</style>
