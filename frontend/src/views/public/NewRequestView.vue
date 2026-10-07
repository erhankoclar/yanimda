<script setup>
import { storeToRefs } from 'pinia'
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import FormAlert from '@/components/public/FormAlert.vue'
import PrimaryButton from '@/components/public/PrimaryButton.vue'
import WizardProgress from '@/components/public/WizardProgress.vue'
import StepContact from '@/components/public/wizard/StepContact.vue'
import StepElder from '@/components/public/wizard/StepElder.vue'
import StepSchedule from '@/components/public/wizard/StepSchedule.vue'
import StepService from '@/components/public/wizard/StepService.vue'
import StepSummary from '@/components/public/wizard/StepSummary.vue'
import { useServices } from '@/composables/useServices'
import { useAuthStore } from '@/stores/auth'
import { WIZARD_STEPS, useRequestWizardStore } from '@/stores/requestWizard'

const STEP_TITLES = [
  'Hangi konuda desteğe ihtiyacınız var?',
  'Destek kimin için?',
  'Ne zaman ve nerede?',
  'Size nasıl ulaşalım?',
  'Son bir kontrol',
]

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const wizard = useRequestWizardStore()
const { step, form, errors, generalError, submitting, isLastStep } = storeToRefs(wizard)
const { services, status: servicesStatus, load: loadServices, nameOf } = useServices()

const heading = ref(null)

onMounted(() => {
  const serviceId = Number(route.query.service) || null
  wizard.start({ serviceId, phone: auth.user?.phone ?? '' })
  loadServices()
})

// Adım değişince odak yeni adımın başlığına taşınır; ekran okuyucu yeni adımı okur.
watch(step, async () => {
  await nextTick()
  heading.value?.focus()
})

/** Geçerliyse sonraki adıma geçer, değilse ilk hatalı alana odaklanır. */
async function goNext() {
  if (!wizard.next()) await focusFirstError()
}

/** Başvuruyu gönderir; başarılıysa başvuru detayına gider. */
async function send() {
  const created = await wizard.submit()
  if (created) {
    await router.push({ name: 'request-detail', params: { id: created.id }, query: { created: '1' } })
  } else {
    await focusFirstError()
  }
}

/** Görünen ilk hatalı alana odaklanır. */
async function focusFirstError() {
  await nextTick()
  document.querySelector('[aria-invalid="true"], .wizard [role="alert"]')?.focus?.()
}
</script>

<template>
  <section class="wizard" aria-labelledby="wizard-step-title">
    <WizardProgress :steps="WIZARD_STEPS" :current="step" />
    <h1 id="wizard-step-title" ref="heading" tabindex="-1">{{ STEP_TITLES[step] }}</h1>

    <form novalidate @submit.prevent="isLastStep ? send() : goNext()">
      <FormAlert :message="generalError" />

      <StepService
        v-if="step === 0"
        v-model="form.service"
        :services="services"
        :status="servicesStatus"
        :error="errors.service"
        @retry="loadServices"
      />
      <StepElder v-else-if="step === 1" :form="form" :errors="errors" />
      <StepSchedule v-else-if="step === 2" :form="form" :errors="errors" />
      <StepContact v-else-if="step === 3" :form="form" :errors="errors" />
      <StepSummary v-else :form="form" :errors="errors" :service-name="nameOf(form.service)" @edit="wizard.goTo" />

      <div class="wizard__nav">
        <PrimaryButton type="submit" block :loading="submitting">
          {{ isLastStep ? 'Başvuruyu gönder' : 'Devam et' }}
        </PrimaryButton>
        <PrimaryButton v-if="step > 0" variant="secondary" block @click="wizard.back">Geri dön</PrimaryButton>
      </div>
    </form>
  </section>
</template>

<style scoped>
.wizard h1 {
  font-size: var(--text-xl);
}

.wizard h1:focus {
  outline: none;
}

.wizard__nav {
  display: grid;
  gap: var(--space-3);
  margin-top: var(--space-6);
}
</style>
