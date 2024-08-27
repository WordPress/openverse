<script setup lang="ts">
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
defineEmits<{ click: [] }>()
</script>

<template>
  <i18n-t
    scope="global"
    class="dmca-notice leading-normal"
    keypath="mediaDetails.contentReport.form.dmca.note"
    tag="p"
  >
    <template #form>
      <VLink
        :aria-label="$t('mediaDetails.contentReport.form.dmca.form')"
        :href="DMCA_FORM_URL"
        class="text-link hover:underline"
        @click="$emit('click')"
        >{{ $t("mediaDetails.contentReport.form.dmca.form") }}</VLink
      >
    </template>
    <template #source>
      <VLink :href="foreignLandingUrl" class="text-link hover:underline">{{
        provider
      }}</VLink>
    </template>
  </i18n-t>
</template>
