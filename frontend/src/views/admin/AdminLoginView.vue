<script setup>
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

import AdminBrand from '@/components/admin/AdminBrand.vue'
import PreferenceControls from '@/components/common/PreferenceControls.vue'
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

// PrimeVue Password, öneri paneli kapalıyken de parola alanına aria-expanded/aria-haspopup
// koyuyor; bunlar type=password için geçersiz olduğundan kaldırılır.
const passwordInputProps = computed(() => ({
  'aria-expanded': null,
  'aria-haspopup': null,
  'aria-invalid': errors.password ? 'true' : 'false',
  'aria-describedby': errors.password ? 'admin-password-error' : undefined,
}))

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
 * Giriş yapar; yönetici olmayan hesabın oturumunu hemen kapatır, yöneticiyi
 * geldiği admin sayfasına (yoksa gösterge paneline) gönderir.
 */
async function submit() {
  generalError.value = ''
  if (!validate()) return
  submitting.value = true
  try {
    await auth.login(form.email, form.password)
    if (!auth.isAdmin) {
      await auth.logout()
      generalError.value = t('admin.login.notStaff')
      return
    }
    const target = safeRedirect(route.query.redirect, '/admin/dashboard')
    // Dönüş adresi admin alanı dışındaysa gösterge paneline gidilir.
    await router.replace(target.startsWith('/admin/') ? target : '/admin/dashboard')
  } catch (error) {
    generalError.value = error?.response?.status === 401
      ? t('admin.login.invalid')
      : parseApiError(error).general
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="admin-auth admin-login">
    <div class="admin-auth__preferences">
      <PreferenceControls />
    </div>

    <main class="admin-login__main">
      <section class="admin-login__card" aria-labelledby="admin-login-title">
        <AdminBrand class="admin-login__brand" />
        <h1 id="admin-login-title">{{ t('admin.login.title') }}</h1>
        <p class="admin-login__intro">{{ t('admin.login.intro') }}</p>

        <form novalidate @submit.prevent="submit">
          <Message v-if="generalError" severity="error" :closable="false" class="admin-login__alert" role="alert">
            {{ generalError }}
          </Message>

          <div class="admin-login__field">
            <label for="admin-email">{{ t('admin.login.email') }}</label>
            <InputText
              id="admin-email"
              v-model="form.email"
              type="email"
              autocomplete="email"
              inputmode="email"
              fluid
              :invalid="!!errors.email"
              :aria-invalid="errors.email ? 'true' : 'false'"
              :aria-describedby="errors.email ? 'admin-email-error' : undefined"
            />
            <small v-if="errors.email" id="admin-email-error" class="admin-login__error">{{ errors.email }}</small>
          </div>

          <div class="admin-login__field">
            <label for="admin-password">{{ t('admin.login.password') }}</label>
            <Password
              v-model="form.password"
              inputId="admin-password"
              :feedback="false"
              toggleMask
              fluid
              autocomplete="current-password"
              :invalid="!!errors.password"
              :inputProps="passwordInputProps"
            />
            <small v-if="errors.password" id="admin-password-error" class="admin-login__error">{{ errors.password }}</small>
          </div>

          <Button type="submit" :label="t('admin.login.submit')" :loading="submitting" fluid />
        </form>

        <a href="/" class="admin-login__back">
          <i class="pi pi-arrow-left" aria-hidden="true" />
          {{ t('admin.login.backToSite') }}
        </a>
      </section>
    </main>
  </div>
</template>

<style scoped>
.admin-login {
  display: flex;
  flex-direction: column;
}

.admin-login__main {
  display: grid;
  flex: 1;
  place-items: center;
  padding: 0 1rem 3rem;
}

.admin-login__card {
  width: 100%;
  max-width: 26rem;
  padding: 2rem 1.5rem;
  border: 1px solid var(--admin-line);
  border-top: 4px solid var(--admin-primary);
  border-radius: var(--admin-radius);
  background: var(--admin-surface);
  box-shadow: var(--admin-shadow);
}

.admin-login__brand {
  margin-bottom: 1.5rem;
}

.admin-login__card h1 {
  font-size: 1.6rem;
}

.admin-login__intro {
  margin: 0.4rem 0 1.5rem;
  color: var(--admin-ink-soft);
}

.admin-login__alert {
  margin-bottom: 1rem;
}

.admin-login__field {
  display: grid;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.admin-login__field label {
  font-weight: 700;
}

.admin-login__error {
  color: var(--admin-danger);
}

.admin-login__back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 1.25rem;
  color: var(--admin-ink-soft);
  font-weight: 700;
  text-decoration: none;
}

.admin-login__back:hover {
  color: var(--admin-primary);
}

@media (min-width: 30rem) {
  .admin-login__card {
    padding: 2.25rem 2rem;
  }
}
</style>
