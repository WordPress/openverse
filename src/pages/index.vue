<template>
  <main
    class="index flex w-full flex-shrink-0 flex-grow flex-col justify-center gap-6 lg:flex-row lg:items-center lg:gap-0"
    :class="
      isNewHeaderEnabled
        ? 'flex-grow px-6 sm:px-0'
        : 'h-screen h-[100dvh] overflow-hidden bg-yellow'
    "
  >
    <VHomepageContent
      v-if="isNewHeaderEnabled"
      class="sm:px-14 md:px-20 lg:px-26 xl:w-[53.375rem] xl:pe-0"
      :handle-search="handleSearch"
      :search-type="searchType"
      :set-search-type="setSearchType"
      :is-sm="isSm"
    />

    <!-- TODO: Refine min-width for different breakpoints, remove magic numbers -->
    <VOldHomepageContent
      v-else
      :handle-search="handleSearch"
      :is-desktop-layout="isDesktopLayout"
      :search-type="searchType"
      :set-search-type="setSearchType"
    />

    <!-- Image carousel -->
    <VHomeGallery
      v-if="isNewHeaderEnabled"
      class="hidden h-full flex-grow xl:flex"
    />
    <VImageCarousel v-else />
    <!-- Disclaimer as footer for small screens -->
    <i18n
      v-if="!isNewHeaderEnabled"
      path="hero.disclaimer.content"
      tag="p"
      class="mt-auto p-6 text-sr lg:hidden"
    >
      <template #openverse>Openverse</template>
      <template #license>
        <VLink
          href="https://creativecommons.org/licenses/"
          class="text-dark-charcoal underline hover:text-dark-charcoal"
          >{{ $t("hero.disclaimer.license") }}</VLink
        >
      </template>
    </i18n>
  </main>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  onMounted,
  ref,
  useMeta,
  useRouter,
} from "@nuxtjs/composition-api"

import {
  ALL_MEDIA,
  SupportedSearchType,
  supportedSearchTypes,
} from "~/constants/media"
import { useLayout } from "~/composables/use-layout"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import VLink from "~/components/VLink.vue"
import VSearchTypePopoverOld from "~/components/VContentSwitcherOld/VSearchTypePopoverOld.vue"
import VImageCarousel from "~/components/VImageCarousel.vue"
import VOldHomepageContent from "~/components/VOldHomepageContent.vue"

export default defineComponent({
  name: "HomePage",
  components: {
    VOldHomepageContent,
    VHomeGallery: () => import("~/components/VHomeGallery/VHomeGallery.vue"),
    VHomepageContent: () => import("~/components/VHomepageContent.vue"),
    VImageCarousel,
    VLink,
  },
  layout: () => {
    return useFeatureFlagStore().isOn("new_header") ? "default" : "blank"
  },
  setup() {
    const router = useRouter()

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const uiStore = useUiStore()
    const featureFlagStore = useFeatureFlagStore()

    const isNewHeaderEnabled = computed(() =>
      featureFlagStore.isOn("new_header")
    )
    const themeColorMeta = [
      { hid: "theme-color", name: "theme-color", content: "#ffe033" },
    ]
    useMeta({
      meta: isNewHeaderEnabled.value
        ? [...themeColorMeta, { hid: "robots", name: "robots", content: "all" }]
        : themeColorMeta,
    })

    const { updateBreakpoint } = useLayout()

    /**
     * Reset the search type, search term and filters when the user navigates [back] to the homepage.
     */
    onMounted(() => {
      searchStore.$reset()
      mediaStore.$reset()

      updateBreakpoint()
    })

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
    const isSm = computed(() => uiStore.isBreakpoint("sm"))

    const contentSwitcher = ref<InstanceType<
      typeof VSearchTypePopoverOld
    > | null>(null)
    const searchType = ref<SupportedSearchType>(ALL_MEDIA)

    const setSearchType = (type: SupportedSearchType) => {
      searchType.value = type
      if (!isNewHeaderEnabled.value) {
        contentSwitcher.value?.close()
      }
    }

    const handleSearch = (searchTerm: string) => {
      if (!searchTerm) return

      router.push(
        searchStore.updateSearchPath({
          type: searchType.value,
          searchTerm,
        })
      )
    }

    return {
      isDesktopLayout,
      isSm,
      isNewHeaderEnabled,

      contentSwitcher,
      searchType,
      setSearchType,
      supportedSearchTypes,

      handleSearch,
    }
  },
  head: {
    meta: [
      {
        hid: "theme-color",
        name: "theme-color",
        content: "#ffe033",
      },
    ],
  },
})
</script>

<style>
@screen lg {
  .homepage-images {
    transform: translateY(-7.143vh);
  }

  .homepage-image:nth-child(even) {
    transform: translateY(50%);
  }
}

.homepage-image {
  transition-delay: var(--transition-index) !important;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: 0.5s;
}
</style>
