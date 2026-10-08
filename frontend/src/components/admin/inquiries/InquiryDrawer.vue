<script setup>
import Button from 'primevue/button'
import Drawer from 'primevue/drawer'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { formatDateTime } from '@/admin/format'
import ServiceIcon from '@/components/public/ServiceIcon.vue'

const visible = defineModel('visible', { type: Boolean, default: false })

const props = defineProps({
  /** Gösterilen hızlı talep; yüklenirken null. */
  inquiry: { type: Object, default: null },
})

const { t } = useI18n()

// Yanıt e-postası talep konusu ve hizmetle önceden doldurulur.
const mailto = computed(() => {
  if (!props.inquiry) return ''
  const subject = t('admin.inquiries.mailSubject', { service: props.inquiry.service.name })
  return `mailto:${props.inquiry.email}?subject=${encodeURIComponent(subject)}`
})
</script>

<template>
  <Drawer v-model:visible="visible" position="right" class="admin-shell inquiry-drawer" :pt="{ root: { 'aria-labelledby': 'inquiry-drawer-title' } }">
    <template #header>
      <h2 id="inquiry-drawer-title" class="inquiry-drawer__title">{{ inquiry?.full_name }}</h2>
    </template>

    <template v-if="inquiry">
      <dl class="inquiry-drawer__facts">
        <div>
          <dt>{{ t('admin.inquiries.columns.service') }}</dt>
          <dd class="inquiry-drawer__service"><ServiceIcon :name="inquiry.service.icon" />{{ inquiry.service.name }}</dd>
        </div>
        <div>
          <dt>{{ t('admin.inquiries.columns.location') }}</dt>
          <dd>{{ inquiry.location ? `${inquiry.location.neighborhood.name}, ${inquiry.location.district.name}` : t('common.none') }}</dd>
        </div>
        <div>
          <dt>{{ t('admin.inquiries.columns.email') }}</dt>
          <dd>{{ inquiry.email }}</dd>
        </div>
        <div>
          <dt>{{ t('admin.inquiries.columns.created') }}</dt>
          <dd>{{ formatDateTime(inquiry.created_at) }}</dd>
        </div>
      </dl>

      <h3 class="inquiry-drawer__label">{{ t('admin.inquiries.message') }}</h3>
      <p class="inquiry-drawer__message">{{ inquiry.message }}</p>
      <p class="inquiry-drawer__consent">{{ t('admin.inquiries.consent', { time: formatDateTime(inquiry.consent_given_at) }) }}</p>

      <Button as="a" :href="mailto" icon="pi pi-envelope" :label="t('admin.inquiries.reply')" class="inquiry-drawer__reply" />
    </template>
  </Drawer>
</template>

<style>
/* PrimeVue'nun sağ çekmece genişliğini ezmek için seçici daha özeldir; dar ekranda tam genişlik olur. */
.p-drawer-right .p-drawer.inquiry-drawer.admin-shell {
  min-height: 0;
  width: min(30rem, 100vw);
}
</style>

<style scoped>
.inquiry-drawer__title {
  font-size: 1.2rem;
}

.inquiry-drawer__facts {
  display: grid;
  gap: 0.75rem;
  margin: 0 0 1.25rem;
}

.inquiry-drawer__facts dt {
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
  font-weight: 700;
}

.inquiry-drawer__facts dd {
  margin: 0.1rem 0 0;
  overflow-wrap: anywhere;
}

.inquiry-drawer__service {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.inquiry-drawer__service :deep(.service-icon) {
  width: 1.2rem;
  height: 1.2rem;
  color: var(--admin-primary);
}

.inquiry-drawer__label {
  margin-bottom: 0.4rem;
  font-size: 0.95rem;
}

.inquiry-drawer__message {
  margin: 0;
  padding: 0.85rem 1rem;
  border-radius: 0.6rem;
  background: var(--admin-bg);
  white-space: pre-line;
  overflow-wrap: anywhere;
}

.inquiry-drawer__consent {
  margin: 0.6rem 0 1.25rem;
  color: var(--admin-ink-soft);
  font-size: 0.8rem;
}

.inquiry-drawer__reply {
  width: 100%;
  text-decoration: none;
}
</style>
