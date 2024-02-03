<template>
  <div
    id="safety-wall"
    class="relative flex h-full w-full flex-grow items-center justify-center border-t border-dark-charcoal-20 bg-white py-8 text-center"
  >
    <section class="mx-auto max-w-2xl px-8 text-sm leading-relaxed">
      <h1 class="heading-5 mb-2">
        {{ t("sensitiveContent.singleResult.title") }}
      </h1>
      <p class="mb-2">
        {{ t("sensitiveContent.singleResult.explanation") }}
      </p>
      <p v-for="reason in media.sensitivity" :key="reason">
        {{
          t(`sensitiveContent.reasons.${camelCase(reason)}`, {
            openverse: "Openverse",
          })
        }}
      </p>
      <i18n-t
        scope="global"
        tag="p"
        class="mt-2"
        keypath="sensitiveContent.singleResult.learnMore"
      >
        <template #openverse>Openverse</template>
        <template #link>
          <VLink class="text-pink hover:underline" href="/sensitive-content">{{
            t("sensitiveContent.singleResult.link")
          }}</VLink>
          {{ " " }}
        </template>
      </i18n-t>

      <div
        class="mt-6 flex flex-col items-stretch justify-center gap-4 md:flex-row md:gap-6"
      >
        <VButton
          as="VLink"
          size="large"
          variant="filled-dark"
          class="label-bold"
          :href="backToSearchPath || '/'"
          @mousedown="handleBack"
        >
          {{ t("singleResult.back") }}
        </VButton>
        <VButton
          size="large"
          variant="bordered-gray"
          class="label-bold"
          has-icon-end
          @click="handleShow"
        >
          {{ t("sensitiveContent.singleResult.show") }}
          <VIcon name="eye-open" />
        </VButton>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import { useSearchStore } from "~/stores/search"
import { useAnalytics } from "~/composables/use-analytics"
import { camelCase } from "~/utils/case"
import type { AudioDetail, ImageDetail } from "~/types/media"

import VLink from "~/components/VLink.vue"
import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

const props = defineProps<{
  media: AudioDetail | ImageDetail
}>()
const emit = defineEmits(["reveal"])

const {
  $i18n: { t },
} = useNuxtApp()

const searchStore = useSearchStore()
const backToSearchPath = computed(() => searchStore.backToSearchPath)

const { sendCustomEvent } = useAnalytics()
const handleBack = () => {
  sendCustomEvent("GO_BACK_FROM_SENSITIVE_RESULT", {
    id: props.media.id,
    sensitivities: props.media.sensitivity.join(","),
  })
}
const handleShow = () => {
  emit("reveal")
}
</script>

<style scoped>
#safety-wall {
  background: no-repeat url(~/assets/safety-bg.png);
  background-size: 100% 100%;
}
</style>
