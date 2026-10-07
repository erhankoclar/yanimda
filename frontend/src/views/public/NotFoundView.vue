<template>
  <section aria-labelledby="not-found-title">
    <h1 id="not-found-title">Sayfa bulunamadı</h1>
    <p>Aradığınız sayfa taşınmış ya da hiç var olmamış olabilir.</p>
    <p>
      <RouterLink :to="{ name: 'landing' }">Ana sayfaya dönün</RouterLink>
      ya da
      <RouterLink :to="{ name: 'request-list' }">başvurularınıza bakın</RouterLink>.
    </p>
  </section>
</template>
