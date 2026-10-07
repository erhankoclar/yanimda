<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AuthShell from '@/components/public/AuthShell.vue'
import BaseCheckbox from '@/components/public/BaseCheckbox.vue'
import BaseInput from '@/components/public/BaseInput.vue'
import FormAlert from '@/components/public/FormAlert.vue'
import PrimaryButton from '@/components/public/PrimaryButton.vue'
import { useAuthStore } from '@/stores/auth'
import { parseApiError } from '@/utils/apiErrors'
import { safeRedirect } from '@/utils/safeRedirect'

const FIELDS = ['first_name', 'last_name', 'email', 'phone', 'password']

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const form = reactive({ first_name: '', last_name: '', email: '', phone: '', password: '' })
const errors = reactive(Object.fromEntries(FIELDS.map((field) => [field, ''])))
const generalError = ref('')
const submitting = ref(false)
const showPassword = ref(false)

/**
 * Zorunlu alanları ve parola uzunluğunu kontrol eder.
 *
 * @returns {boolean} Form gönderilebilir durumdaysa true.
 */
function validate() {
  errors.first_name = form.first_name.trim() ? '' : 'Adınızı yazın.'
  errors.last_name = form.last_name.trim() ? '' : 'Soyadınızı yazın.'
  errors.email = form.email.trim() ? '' : 'E-posta adresinizi yazın.'
  errors.password = form.password.length >= 8 ? '' : 'Parolanız en az 8 karakter olmalı.'
  errors.phone = ''
  return FIELDS.every((field) => !errors[field])
}

/** Hesabı oluşturur, oturum açar ve kullanıcıyı geldiği sayfaya gönderir. */
async function submit() {
  generalError.value = ''
  if (!validate()) return
  submitting.value = true
  try {
    await auth.register({ ...form, email: form.email.trim() })
    await router.replace(safeRedirect(route.query.redirect, '/requests/new'))
  } catch (error) {
    const parsed = parseApiError(error, FIELDS)
    Object.assign(errors, parsed.fields)
    generalError.value = parsed.general
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthShell title-id="register-title">
    <h1 id="register-title">Kayıt olun</h1>
    <p>Başvurularınızı takip edebilmeniz için kısa bir hesap oluşturalım.</p>

    <form novalidate @submit.prevent="submit">
      <FormAlert :message="generalError" />
      <BaseInput v-model="form.first_name" label="Adınız" autocomplete="given-name" required :error="errors.first_name" />
      <BaseInput v-model="form.last_name" label="Soyadınız" autocomplete="family-name" required :error="errors.last_name" />
      <BaseInput
        v-model="form.email"
        label="E-posta adresi"
        type="email"
        autocomplete="email"
        inputmode="email"
        hint="Girişte bu adresi kullanacaksınız."
        required
        :error="errors.email"
      />
      <BaseInput
        v-model="form.phone"
        label="Telefon"
        type="tel"
        autocomplete="tel"
        inputmode="tel"
        hint="Örnek: 0555 123 45 67"
        :error="errors.phone"
      />
      <BaseInput
        v-model="form.password"
        label="Parola"
        :type="showPassword ? 'text' : 'password'"
        autocomplete="new-password"
        hint="En az 8 karakter. Yalnızca rakamlardan oluşmasın ve kolay tahmin edilmesin."
        required
        :error="errors.password"
      />
      <BaseCheckbox v-model="showPassword">Parolayı göster</BaseCheckbox>
      <PrimaryButton type="submit" block :loading="submitting">Hesabımı oluştur</PrimaryButton>
    </form>

    <p class="auth-page__switch">
      Zaten hesabınız var mı?
      <RouterLink :to="{ name: 'login', query: route.query }">Giriş yapın</RouterLink>
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
