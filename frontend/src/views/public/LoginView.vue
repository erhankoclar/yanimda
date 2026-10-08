<script setup>
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

import AuthShell from '@/components/public/AuthShell.vue'
import BaseInput from '@/components/public/BaseInput.vue'
import FormAlert from '@/components/public/FormAlert.vue'
import PrimaryButton from '@/components/public/PrimaryButton.vue'
import { useAuthStore } from '@/stores/auth'
import { parseApiError } from '@/utils/apiErrors'
import { safeRedirect } from '@/utils/safeRedirect'

const { t } = useI18n()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const generalError = ref('')
const submitting = ref(false)

/**
 * Boş alanları işaretler.
 *
 * @returns {boolean} Form gönderilebilir durumdaysa true.
 */
function validate() {
  errors.email = form.email.trim() ? '' : t('validation.emailRequired')
  errors.password = form.password ? '' : t('validation.passwordRequired')
  return !errors.email && !errors.password
}

/**
 * Giriş yapar; kullanıcıyı geldiği sayfaya, yoksa yöneticiyi yönetim paneline, başvuru sahibini
 * başvurularına gönderir.
 */
async function submit() {
  generalError.value = ''
  if (!validate()) return
  submitting.value = true
  try {
    await auth.login(form.email, form.password)
    await router.replace(safeRedirect(route.query.redirect, auth.isAdmin ? '/admin/dashboard' : '/requests'))
  } catch (error) {
    generalError.value = error?.response?.status === 401
      ? t('auth.login.invalid')
      : parseApiError(error).general
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthShell title-id="login-title">
    <h1 id="login-title">{{ t('auth.login.title') }}</h1>
    <p>{{ t('auth.login.intro') }}</p>

    <form novalidate @submit.prevent="submit">
      <FormAlert :message="generalError" />
      <BaseInput
        v-model="form.email"
        :label="t('auth.login.email')"
        type="email"
        autocomplete="email"
        inputmode="email"
        required
        :error="errors.email"
      />
      <BaseInput
        v-model="form.password"
        :label="t('auth.login.password')"
        type="password"
        autocomplete="current-password"
        required
        :error="errors.password"
      />
      <PrimaryButton type="submit" block :loading="submitting">{{ t('auth.login.submit') }}</PrimaryButton>
    </form>

    <p class="auth-page__switch">
      {{ t('auth.login.noAccount') }}
      <RouterLink :to="{ name: 'register', query: route.query }">{{ t('auth.login.register') }}</RouterLink>
    </p>
  </AuthShell>
</template>

<style scoped>
form {
  margin-top: var(--space-5);
}

.auth-page__switch {
  margin-top: var(--space-5);
}
</style>
