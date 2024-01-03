<template>
  <main
    class="index flex w-full flex-shrink-0 flex-grow flex-col justify-center gap-6 px-6 sm:px-0 lg:flex-row lg:items-center lg:gap-0"
  >
    <VHomepageContent
      class="sm:px-14 md:px-20 lg:px-26 xl:w-[53.375rem] xl:pe-0"
      :handle-search="handleSearch"
      :search-type="searchType"
      :set-search-type="setSearchType"
    />

    <!-- Image carousel -->
    <VHomeGallery v-if="isXl" class="flex h-full flex-grow" />
  </main>
</template>

<script lang="ts">
import { defineNuxtComponent, useHead } from "#imports"

import { computed, onMounted, ref } from "vue"

import { useRouter } from "@nuxtjs/composition-api"

import {
  ALL_MEDIA,
  isAdditionalSearchType,
  isSupportedMediaType,
  SearchType,
  supportedSearchTypes,
} from "~/constants/media"
import { useAnalytics } from "~/composables/use-analytics"
import { useLayout } from "~/composables/use-layout"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { useFeatureFlagStore } from "~/stores/feature-flag"

import VHomeGallery from "~/components/VHomeGallery/VHomeGallery.vue"
import VHomepageContent from "~/components/VHomepageContent.vue"

export default defineNuxtComponent({
  name: "HomePage",
  components: {
    VHomeGallery,
    VHomepageContent,
  },
  setup() {
    const router = useRouter()

    const featureFlagStore = useFeatureFlagStore()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const uiStore = useUiStore()

    const { sendCustomEvent } = useAnalytics()

    useHead({
      meta: [
        { name: "theme-color", content: "#ffe033" },
        { name: "robots", content: "all" },
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

    const isXl = computed(() => uiStore.isBreakpoint("xl"))

    const searchType = ref<SearchType>(ALL_MEDIA)

    const setSearchType = (type: SearchType) => {
      if (type === ALL_MEDIA || isSupportedMediaType(type)) {
        searchType.value = type
      } else if (
        featureFlagStore.isOn("additional_search_types") &&
        isAdditionalSearchType(type)
      ) {
        searchType.value = type
      }
    }

    const handleSearch = (searchTerm: string) => {
      sendCustomEvent("SUBMIT_SEARCH", {
        searchType: searchType.value,
        query: searchTerm,
      })

      router.push(
        searchStore.updateSearchPath({
          type: searchType.value,
          searchTerm,
        })
      )
    }

    return {
      isXl,

      searchType,
      setSearchType,
      supportedSearchTypes,

      handleSearch,
    }
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
