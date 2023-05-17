<template>
  <div>
    <div v-show="showBanners" class="flex flex-col gap-3 p-3 pb-0">
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
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"

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

    const showBanners = computed(
      () => shouldShowMigrationBanner.value || shouldShowTranslationBanner.value
    )

    return {
      translationBannerId,
      shouldShowMigrationBanner,
      shouldShowTranslationBanner,
      showBanners,
      dismissBanner,
    }
  },
})
</script>
