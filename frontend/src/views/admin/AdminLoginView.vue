<script setup>
import PreferenceControls from '@/components/common/PreferenceControls.vue'
</script>

<template>
  <section class="admin-auth">
    <div class="admin-auth__preferences">
      <PreferenceControls />
    </div>
    <h1>{{ $t('admin.titles.login') }}</h1>
  </section>
</template>
