<template>
  <span class="admin-brand">
    <svg class="admin-brand__icon" viewBox="0 0 40 40" aria-hidden="true" focusable="false">
      <circle cx="20" cy="20" r="20" class="admin-brand__bg" />
      <path d="M11 17.5c0-3.6 2.8-6.5 6.3-6.5 1.1 0 2 .4 2.7 1 .7-.6 1.6-1 2.7-1 3.5 0 6.3 2.9 6.3 6.5 0 6-9 11.5-9 11.5s-9-5.5-9-11.5Z" class="admin-brand__heart" />
    </svg>
    <span class="admin-brand__text">{{ $t('admin.brand') }}</span>
  </span>
</template>

<style scoped>
.admin-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}

.admin-brand__icon {
  flex: none;
  width: 2rem;
  height: 2rem;
}

.admin-brand__bg {
  fill: var(--admin-primary);
}

.admin-brand__heart {
  fill: var(--admin-accent);
}

.admin-brand__text {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif;
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}
</style>
