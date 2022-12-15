<template>
  <div>
    <VMigrationNotice
      v-if="shouldShowMigrationBanner"
      @close="dismissBanner('cc-referral')"
    />
    <VTranslationStatusBanner
      v-if="shouldShowTranslationBanner"
      :banner-key="translationBannerId"
      @close="dismissBanner(translationBannerId)"
    />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api"

import { useUiStore } from "~/stores/ui"
import type { TranslationBannerId } from "~/types/banners"

export default defineComponent({
  name: "VBanners",
  components: {
    VMigrationNotice: () => import("~/components/VBanner/VMigrationNotice.vue"),
    VTranslationStatusBanner: () =>
      import("~/components/VBanner/VTranslationStatusBanner.vue"),
  },
  setup() {
    const uiStore = useUiStore()
    const shouldShowMigrationBanner = computed(
      () => uiStore.shouldShowMigrationBanner
    )
    const shouldShowTranslationBanner = computed(
      () => uiStore.shouldShowTranslationBanner
    )

    const translationBannerId = computed<TranslationBannerId>(
      () => uiStore.translationBannerId
    )

    const dismissBanner = (bannerKey: TranslationBannerId) => {
      uiStore.dismissBanner(bannerKey)
    }

    return {
      translationBannerId,
      shouldShowMigrationBanner,
      shouldShowTranslationBanner,

      dismissBanner,
    }
  },
})
</script>
