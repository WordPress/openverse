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
    </div>
  </div>
</template>

<script lang="ts">
import { defineAsyncComponent } from "#imports"

import { computed, defineComponent } from "vue"

import { useUiStore } from "~/stores/ui"
import usePages from "~/composables/use-pages"

import type { TranslationBannerId, BannerId } from "~/types/banners"

export default defineComponent({
  name: "VBanners",
  components: {
    VTranslationStatusBanner: defineAsyncComponent(
      () => import("~/components/VBanner/VTranslationStatusBanner.vue")
    ),
    VAnalyticsNotice: defineAsyncComponent(
      () => import("~/components/VBanner/VAnalyticsNotice.vue")
    ),
  },
  setup() {
    const uiStore = useUiStore()

    const shouldShowTranslationBanner = computed(
      () => uiStore.shouldShowTranslationBanner
    )
    const shouldShowAnalyticsBanner = computed(
      () => uiStore.shouldShowAnalyticsBanner
    )

    const translationBannerId = computed<TranslationBannerId>(
      () => uiStore.translationBannerId
    )

    const { current: currentPage } = usePages()
    const variant = computed(() =>
      ["", "index"].includes(currentPage.value) ? "dark" : "regular"
    )

    const dismissBanner = (bannerKey: BannerId) => {
      uiStore.dismissBanner(bannerKey)
    }

    const showBanners = computed(() =>
      [shouldShowTranslationBanner, shouldShowAnalyticsBanner].some(
        (item) => item.value
      )
    )

    return {
      translationBannerId,
      shouldShowTranslationBanner,
      shouldShowAnalyticsBanner,
      showBanners,
      dismissBanner,
      variant,
    }
  },
})
</script>
