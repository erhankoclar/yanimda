<script setup>
import PreferenceControls from '@/components/common/PreferenceControls.vue'
</script>

<template>
  <div class="admin-shell admin-layout" data-layout="admin">
    <aside class="admin-layout__sidebar">
      <span class="admin-layout__brand">Yanımda Yönetim</span>
    </aside>
    <div class="admin-layout__main">
      <header class="admin-layout__topbar">
        <PreferenceControls />
      </header>
      <main class="admin-layout__content">
        <RouterView />
      </main>
    </div>
  </div>
</template>
