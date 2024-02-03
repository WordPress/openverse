<template>
  <VNotificationBanner
    :id="bannerKey"
    nature="warning"
    data-testid="banner-translation"
    :close-button-label="t('notification.translation.close')"
    @close="$emit('close')"
  >
    <i18n-t scope="global" keypath="notification.translation.text" tag="span">
      <template #link>
        <VLink :href="currentLocale.link" class="text-curr underline">{{
          t("notification.translation.link")
        }}</VLink>
      </template>
      <template #locale>
        {{ currentLocale.name }}
      </template>
    </i18n-t>
  </VNotificationBanner>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import type { BannerId } from "~/types/banners"

import { createTranslationLink } from "~/utils/translation-banner"

import VLink from "~/components/VLink.vue"
import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"

import type { LocaleObject } from "@nuxtjs/i18n"

defineProps<{
  bannerKey: BannerId
}>()
defineEmits(["close"])

const { $i18n } = useNuxtApp()
const { t } = $i18n

/**
 * Returns the link to the GlotPress project for the current locale and the locale native name.
 */
const currentLocale = computed(() => {
  const localeObject = $i18n.localeProperties.value as LocaleObject

  return {
    link: createTranslationLink(localeObject),
    name: localeObject.name,
  }
})
</script>
