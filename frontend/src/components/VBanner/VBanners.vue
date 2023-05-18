<template>
  <div>
    <div v-show="showBanners" class="flex flex-col gap-2 p-2 pb-0">
      <VMigrationNotice
        v-if="shouldShowMigrationBanner"
        :variant="variant"
        @close="dismissBanner('cc-referral')"
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
import { computed, defineComponent } from "vue"

import { useUiStore } from "~/stores/ui"
import usePages from "~/composables/use-pages"

import type { TranslationBannerId, BannerId } from "~/types/banners"

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

    const { current: currentPage } = usePages()
    const variant = computed(() =>
      currentPage.value === "index" ? "dark" : "regular"
    )

    const dismissBanner = (bannerKey: BannerId) => {
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
      variant,
    }
  },
})
</script>
