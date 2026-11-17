<script setup lang="ts">
import { defineAsyncComponent, useNuxtApp } from "#imports"
import { computed } from "vue"

import type { TranslationBannerId, BannerId } from "#shared/types/banners"
import { useUiStore } from "~/stores/ui"
import usePages from "~/composables/use-pages"

import type { LocaleObject } from "@nuxtjs/i18n"

const VTranslationStatusBanner = defineAsyncComponent(
  () => import("~/components/VBanner/VTranslationStatusBanner.vue")
)
const VAnalyticsNotice = defineAsyncComponent(
  () => import("~/components/VBanner/VAnalyticsNotice.vue")
)
const VUnsupportedLocaleBanner = defineAsyncComponent(
  () => import("~/components/VBanner/VUnsupportedLocaleBanner.vue")
)
const uiStore = useUiStore()
const localeProperties = useNuxtApp().$i18n.localeProperties

const shouldShowTranslationBanner = computed(() =>
  uiStore.shouldShowTranslationBanner(localeProperties.value as LocaleObject)
)
const shouldShowAnalyticsBanner = computed(
  () => uiStore.shouldShowAnalyticsBanner
)
const shouldShowUnsupportedLocaleBanner = computed(
  () => uiStore.shouldShowUnsupportedLocaleBanner
)

const translationBannerId = computed<TranslationBannerId>(
  () => `translation-${localeProperties.value.code}`
)

const { current: currentPage } = usePages()
const variant = computed(() =>
  ["", "index"].includes(currentPage.value) ? "dark" : "regular"
)

const dismissBanner = (bannerKey: BannerId) => {
  uiStore.dismissBanner(bannerKey)
}

// The unsupported-locale banner is a one-time popup rather than a permanently
// dismissible banner, so closing it just hides the current instance.
const closeUnsupportedLocaleBanner = () => {
  uiStore.setUnsupportedLocaleBannerVisible(false)
}

const showBanners = computed(() =>
  [
    shouldShowTranslationBanner,
    shouldShowAnalyticsBanner,
    shouldShowUnsupportedLocaleBanner,
  ].some((item) => item.value)
)
</script>

<template>
  <div>
    <div v-show="showBanners" class="flex flex-col gap-2 p-2 pb-0">
      <VAnalyticsNotice
        v-if="shouldShowAnalyticsBanner"
        :variant="variant"
        @close="dismissBanner('analytics')"
      />
      <VTranslationStatusBanner
        v-if="shouldShowTranslationBanner"
        :variant="variant"
        :banner-key="translationBannerId"
        @close="dismissBanner(translationBannerId)"
      />
      <VUnsupportedLocaleBanner
        v-if="shouldShowUnsupportedLocaleBanner"
        :variant="variant"
        @close="closeUnsupportedLocaleBanner"
      />
    </div>
  </div>
</template>
