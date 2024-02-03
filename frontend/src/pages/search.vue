<template>
  <VErrorSection
    v-if="fetchingError"
    :fetching-error="fetchingError"
    class="w-full py-10"
  />
  <section v-else>
    <header v-if="supported" class="my-0 md:mb-8 md:mt-4">
      <VSearchResultsTitle :size="isAllView ? 'large' : 'default'">{{
        searchTerm
      }}</VSearchResultsTitle>
    </header>
    <NuxtPage
      v-if="supported"
      :key="$route.path"
      :results="results"
      :search-term="searchTerm"
      data-testid="search-results"
    />
    <VGridSkeleton
      v-if="isFetching && !results.length"
      :is-sidebar-visible="isFilterSidebarVisible"
      :is-for-tab="isSearchTypeSupported(searchType) ? searchType : 'all'"
    />
    <footer :class="isAllView ? 'mb-6 mt-4 lg:mb-10' : 'mt-4'">
      <VLoadMore
        v-if="isSearchTypeSupported(searchType)"
        :is-fetching="isFetching"
        :search-term="searchTerm"
        :search-type="searchType"
        @load-more="handleLoadMore"
      />
    </footer>
    <VExternalSearchForm
      v-if="!isAllView"
      :search-term="searchTerm"
      :is-supported="supported"
      :has-no-results="false"
    />
    <VScrollButton
      v-show="showScrollButton"
      :is-filter-sidebar-visible="isFilterSidebarVisible"
      data-testid="scroll-button"
    />
  </section>
</template>

<script setup lang="ts">
import {
  definePageMeta,
  isSearchTypeSupported,
  useAsyncSearch,
  useHead,
  useNuxtApp,
} from "#imports"

import { computed, inject, ref, watch } from "vue"
import { storeToRefs } from "pinia"

import { searchMiddleware } from "~/middleware/search"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { ALL_MEDIA, isSupportedMediaType } from "~/constants/media"

import { IsHeaderScrolledKey, IsSidebarVisibleKey } from "~/types/provides"

import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"
import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"
import VScrollButton from "~/components/VScrollButton.vue"
import VExternalSearchForm from "~/components/VExternalSearch/VExternalSearchForm.vue"
import VLoadMore from "~/components/VLoadMore.vue"
import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"

definePageMeta({
  layout: "search-layout",
  middleware: searchMiddleware,
})
const mediaStore = useMediaStore()
const searchStore = useSearchStore()

const {
  searchTerm,
  searchType,
  searchTypeIsSupported: supported,
} = storeToRefs(searchStore)

const isFilterSidebarVisible = inject(IsSidebarVisibleKey, ref(false))
const showScrollButton = inject(IsHeaderScrolledKey, ref(false))

// I don't know *exactly* why this is necessary, but without it
// transitioning from the homepage to this page breaks the
// watcher in useStorage and recent searches won't be saved
// properly. It is something related to Pinia, Nuxt SSR,
// hydration and Vue reactives. Hopefully fixed in Nuxt 3.
searchStore.refreshRecentSearches()

const results = computed(() => {
  const st = searchType.value
  return st === ALL_MEDIA
    ? mediaStore.allMedia
    : isSupportedMediaType(st)
    ? mediaStore.resultItems[st]
    : []
})

const isAllView = computed(() => searchType.value === ALL_MEDIA)

const pageTitle = ref(`${searchTerm.value} | Openverse`)
watch(searchTerm, () => {
  pageTitle.value = `${searchTerm.value} | Openverse`
})
const i18n = useNuxtApp().$i18n

const lang = computed(() => {
  const lp = i18n.localeProperties.value
  return {
    lang: lp.code,
    dir: lp.dir,
  }
})

useHead({
  title: pageTitle.value,
  meta: [{ key: "robots", name: "robots", content: "all" }],
  htmlAttrs: lang.value,
})

const { handleLoadMore, fetchingError, isFetching } = await useAsyncSearch()
</script>
