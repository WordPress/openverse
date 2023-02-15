<template>
  <main
    class="index flex w-full flex-shrink-0 flex-grow flex-grow flex-col justify-center gap-6 px-6 sm:px-0 lg:flex-row lg:items-center lg:gap-0"
  >
    <VHomepageContent
      class="sm:px-14 md:px-20 lg:px-26 xl:w-[53.375rem] xl:pe-0"
      :handle-search="handleSearch"
      :search-type="searchType"
      :set-search-type="setSearchType"
      :is-sm="isSm"
    />

    <!-- Image carousel -->
    <VHomeGallery class="hidden h-full flex-grow xl:flex" />
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

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

export default defineComponent({
  name: "HomePage",
  components: {
    VHomeGallery: () => import("~/components/VHomeGallery/VHomeGallery.vue"),
    VHomepageContent: () => import("~/components/VHomepageContent.vue"),
  },
  setup() {
    const router = useRouter()

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const uiStore = useUiStore()

    useMeta({
      meta: [
        { hid: "theme-color", name: "theme-color", content: "#ffe033" },
        { hid: "robots", name: "robots", content: "all" },
      ],
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

    const searchType = ref<SupportedSearchType>(ALL_MEDIA)

    const setSearchType = (type: SupportedSearchType) => {
      searchType.value = type
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

      searchType,
      setSearchType,
      supportedSearchTypes,

      handleSearch,
    }
  },
  head: {},
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
