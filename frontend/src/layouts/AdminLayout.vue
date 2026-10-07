<template>
  <div class="admin-layout" data-layout="admin">
    <aside class="admin-layout__sidebar">
      <span class="admin-layout__brand">Yanımda Yönetim</span>
    </aside>
    <div class="admin-layout__main">
      <header class="admin-layout__topbar" />
      <main class="admin-layout__content">
        <RouterView />
      </main>
    </div>
  </div>
</template>
