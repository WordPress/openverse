<template>
  <VNotificationBanner
    id="analytics"
    nature="info"
    :close-button-label="t('notification.analytics.close')"
    @close="$emit('close')"
  >
    <i18n-t scope="global" tag="span" keypath="notification.analytics.text">
      <template #link>
        <VLink :href="privacyPath" class="text-curr underline">{{
          t("notification.analytics.link")
        }}</VLink>
      </template>
    </i18n-t>
  </VNotificationBanner>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import VLink from "~/components/VLink.vue"
import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"

defineEmits(["close"])
const {
  $i18n: { t },
  $localePath,
} = useNuxtApp()
const privacyPath = computed(() => $localePath("/privacy"))
</script>
