<script setup>
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
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

const { t } = useI18n()
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
  errors.first_name = form.first_name.trim() ? '' : t('validation.register.firstName')
  errors.last_name = form.last_name.trim() ? '' : t('validation.register.lastName')
  errors.email = form.email.trim() ? '' : t('validation.emailRequired')
  errors.password = form.password.length >= 8 ? '' : t('validation.register.passwordMin')
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
    <h1 id="register-title">{{ t('auth.register.title') }}</h1>
    <p>{{ t('auth.register.intro') }}</p>

    <form novalidate @submit.prevent="submit">
      <FormAlert :message="generalError" />
      <BaseInput v-model="form.first_name" :label="t('auth.register.firstName')" autocomplete="given-name" required :error="errors.first_name" />
      <BaseInput v-model="form.last_name" :label="t('auth.register.lastName')" autocomplete="family-name" required :error="errors.last_name" />
      <BaseInput
        v-model="form.email"
        :label="t('auth.register.email')"
        type="email"
        autocomplete="email"
        inputmode="email"
        :hint="t('auth.register.emailHint')"
        required
        :error="errors.email"
      />
      <BaseInput
        v-model="form.phone"
        :label="t('auth.register.phone')"
        type="tel"
        autocomplete="tel"
        inputmode="tel"
        :hint="t('auth.register.phoneHint')"
        :error="errors.phone"
      />
      <BaseInput
        v-model="form.password"
        :label="t('auth.register.password')"
        :type="showPassword ? 'text' : 'password'"
        autocomplete="new-password"
        :hint="t('auth.register.passwordHint')"
        required
        :error="errors.password"
      />
      <BaseCheckbox v-model="showPassword">{{ t('auth.register.showPassword') }}</BaseCheckbox>
      <PrimaryButton type="submit" block :loading="submitting">{{ t('auth.register.submit') }}</PrimaryButton>
    </form>

    <p class="auth-page__switch">
      {{ t('auth.register.haveAccount') }}
      <RouterLink :to="{ name: 'login', query: route.query }">{{ t('auth.register.login') }}</RouterLink>
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
