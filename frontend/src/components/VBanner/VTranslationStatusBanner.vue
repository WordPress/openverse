<template>
  <VNotificationBanner
    :id="bannerKey"
    nature="warning"
    data-testid="banner-translation"
    :close-button-label="$t('notification.translation.close')"
    @close="$emit('close')"
  >
    <i18n-t scope="global" keypath="notification.translation.text" tag="span">
      <template #link>
        <VLink :href="currentLocale.link" class="text-curr underline">{{
          $t("notification.translation.link")
        }}</VLink>
      </template>
      <template #locale>
        {{ currentLocale.name }}
      </template>
    </i18n-t>
  </VNotificationBanner>
</template>

<script lang="ts">
import { useI18n } from "#imports"

import { computed, defineComponent, PropType } from "vue"

import type { BannerId } from "~/types/banners"

import { createTranslationLink } from "~/utils/translation-banner"

import { defineEvent } from "~/types/emits"

import VLink from "~/components/VLink.vue"
import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"

import type { LocaleObject } from "@nuxtjs/i18n"

export default defineComponent({
  name: "VTranslationStatusBanner",
  components: {
    VLink,
    VNotificationBanner,
  },
  props: {
    bannerKey: {
      type: String as PropType<BannerId>,
      required: true,
    },
  },
  emits: {
    close: defineEvent(),
  },
  setup() {
    /**
     * Returns the link to the GlotPress project for the current locale and the locale native name.
     */
    const currentLocale = computed(() => {
      const localeObject = useI18n({ useScope: "global" }).localeProperties
        .value as LocaleObject

      return {
        link: createTranslationLink(localeObject),
        name: localeObject.name,
      }
    })

    return {
      currentLocale,
    }
  },
})
</script>
