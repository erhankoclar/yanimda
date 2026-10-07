<template>
  <span class="brand-mark">
    <svg class="brand-mark__icon" viewBox="0 0 40 40" aria-hidden="true" focusable="false">
      <circle cx="20" cy="20" r="20" class="brand-mark__bg" />
      <path d="M11 17.5c0-3.6 2.8-6.5 6.3-6.5 1.1 0 2 .4 2.7 1 .7-.6 1.6-1 2.7-1 3.5 0 6.3 2.9 6.3 6.5 0 6-9 11.5-9 11.5s-9-5.5-9-11.5Z" class="brand-mark__heart" />
    </svg>
    <span class="brand-mark__text">Yanımda</span>
  </span>
</template>

<style scoped>
.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.brand-mark__icon {
  width: 2.25rem;
  height: 2.25rem;
}

.brand-mark__bg {
  fill: var(--color-primary);
}

.brand-mark__heart {
  fill: var(--color-accent);
}


.brand-mark__text {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}
</style>
