<script setup lang="ts">
import type { BannerVariant } from "#shared/constants/banners"
import { BASE_URL } from "#shared/utils/translation-banner"

import VLink from "~/components/VLink.vue"
import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"

defineProps<{
  variant?: BannerVariant
}>()

defineEmits<{
  close: []
}>()

// Link to the general Openverse project page, where the user can find or start
// a translation for their language, rather than the English one.
const translationLink = BASE_URL
</script>

<template>
  <VNotificationBanner
    id="unsupported-locale"
    nature="warning"
    :variant="variant"
    :close-button-label="$t('notification.unsupportedLocale.close')"
    @close="$emit('close')"
  >
    <i18n-t
      scope="global"
      tag="span"
      keypath="notification.unsupportedLocale.text"
    >
      <template #link>
        <VLink :href="translationLink" class="text-curr underline">{{
          $t("notification.unsupportedLocale.link")
        }}</VLink>
      </template>
    </i18n-t>
  </VNotificationBanner>
</template>
