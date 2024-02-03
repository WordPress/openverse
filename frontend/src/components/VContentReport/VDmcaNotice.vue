<template>
  <i18n-t
    scope="global"
    class="dmca-notice"
    keypath="mediaDetails.contentReport.form.dmca.note"
    tag="p"
  >
    <template #form>
      <VLink
        :aria-label="t('mediaDetails.contentReport.form.dmca.form')"
        :href="DMCA_FORM_URL"
        class="text-pink hover:underline"
        @click="emit('click')"
        >{{ t("mediaDetails.contentReport.form.dmca.form") }}</VLink
      >
    </template>
    <template #source>
      <VLink :href="foreignLandingUrl" class="text-pink hover:underline">{{
        provider
      }}</VLink>
    </template>
  </i18n-t>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { DMCA_FORM_URL } from "~/constants/content-report"

import VLink from "~/components/VLink.vue"

defineProps<{
  /**
   * the foreign landing URL for the media item
   */
  foreignLandingUrl: string
  /**
   * the name of the provider of the media item
   */
  provider: string
}>()

const emit = defineEmits<{
  click: []
}>()

const {
  $i18n: { t },
} = useNuxtApp()
</script>
