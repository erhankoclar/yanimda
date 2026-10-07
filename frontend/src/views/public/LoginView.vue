<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AuthShell from '@/components/public/AuthShell.vue'
import BaseInput from '@/components/public/BaseInput.vue'
import FormAlert from '@/components/public/FormAlert.vue'
import PrimaryButton from '@/components/public/PrimaryButton.vue'
import { useAuthStore } from '@/stores/auth'
import { parseApiError } from '@/utils/apiErrors'
import { safeRedirect } from '@/utils/safeRedirect'

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
  errors.email = form.email.trim() ? '' : 'E-posta adresinizi yazın.'
  errors.password = form.password ? '' : 'Parolanızı yazın.'
  return !errors.email && !errors.password
}

/** Giriş yapar ve kullanıcıyı geldiği sayfaya (yoksa başvurularına) gönderir. */
async function submit() {
  generalError.value = ''
  if (!validate()) return
  submitting.value = true
  try {
    await auth.login(form.email, form.password)
    await router.replace(safeRedirect(route.query.redirect, '/requests'))
  } catch (error) {
    generalError.value = error?.response?.status === 401
      ? 'E-posta adresi veya parola hatalı. Lütfen kontrol edip tekrar deneyin.'
      : parseApiError(error).general
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthShell title-id="login-title">
    <h1 id="login-title">Giriş yap</h1>
    <p>Başvurunuzu sürdürmek ve durumunu görmek için hesabınıza girin.</p>

    <form novalidate @submit.prevent="submit">
      <FormAlert :message="generalError" />
      <BaseInput
        v-model="form.email"
        label="E-posta adresi"
        type="email"
        autocomplete="email"
        inputmode="email"
        required
        :error="errors.email"
      />
      <BaseInput
        v-model="form.password"
        label="Parola"
        type="password"
        autocomplete="current-password"
        required
        :error="errors.password"
      />
      <PrimaryButton type="submit" block :loading="submitting">Giriş yap</PrimaryButton>
    </form>

    <p class="auth-page__switch">
      Hesabınız yok mu?
      <RouterLink :to="{ name: 'register', query: route.query }">Kayıt olun</RouterLink>
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
