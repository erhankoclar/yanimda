<script setup>
defineProps({
  /** Bayrak: `tr` (Türkiye) veya `en` (Birleşik Krallık). */
  code: { type: String, required: true },
})
</script>

<template>
  <svg v-if="code === 'tr'" class="flag-icon" viewBox="0 0 30 20" aria-hidden="true" focusable="false">
    <rect width="30" height="20" fill="#e30a17" />
    <circle cx="11.25" cy="10" r="5" fill="#fff" />
    <circle cx="12.5" cy="10" r="4" fill="#e30a17" />
    <polygon
      fill="#fff"
      points="15.8,10 18.02,10.72 18.02,13.06 19.39,11.17 21.62,11.89 20.24,10 21.62,8.11 19.39,8.83 18.02,6.94 18.02,9.28"
      transform="rotate(0 18.7 10)"
    />
  </svg>
  <svg v-else class="flag-icon" viewBox="0 0 60 30" aria-hidden="true" focusable="false">
    <clipPath id="flag-uk-clip"><path d="M0,0 v30 h60 v-30 z" /></clipPath>
    <clipPath id="flag-uk-diagonal"><path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z" /></clipPath>
    <g clip-path="url(#flag-uk-clip)">
      <path d="M0,0 v30 h60 v-30 z" fill="#012169" />
      <path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6" />
      <path d="M0,0 L60,30 M60,0 L0,30" clip-path="url(#flag-uk-diagonal)" stroke="#c8102e" stroke-width="4" />
      <path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10" />
      <path d="M30,0 v30 M0,15 h60" stroke="#c8102e" stroke-width="6" />
    </g>
  </svg>
</template>

<style scoped>
.flag-icon {
  display: block;
  width: 1.5rem;
  height: 1rem;
  border-radius: 2px;
  box-shadow: 0 0 0 1px rgb(0 0 0 / 0.12);
}
</style>
