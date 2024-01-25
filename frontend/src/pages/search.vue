<template>
  <section>
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
      v-if="fetchState.isFetching && !results.length"
      :is-sidebar-visible="isFilterSidebarVisible"
      :is-for-tab="isSearchTypeSupported(searchType) ? searchType : 'all'"
    />
  </section>
</template>

<script setup lang="ts">
import { definePageMeta, isSearchTypeSupported } from "#imports"

import { computed, inject, ref, watch } from "vue"
import { storeToRefs } from "pinia"

import { searchMiddleware } from "~/middleware/search"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { ALL_MEDIA, isSupportedMediaType } from "~/constants/media"

import { IsSidebarVisibleKey } from "~/types/provides"

import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"
import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"

definePageMeta({
  layout: "search-layout",
  middleware: searchMiddleware,
})
const mediaStore = useMediaStore()
const searchStore = useSearchStore()

const isFilterSidebarVisible = inject(IsSidebarVisibleKey, ref(false))

// I don't know *exactly* why this is necessary, but without it
// transitioning from the homepage to this page breaks the
// watcher in useStorage and recent searches won't be saved
// properly. It is something related to Pinia, Nuxt SSR,
// hydration and Vue reactives. Hopefully fixed in Nuxt 3.
searchStore.refreshRecentSearches()

const {
  searchTerm,
  searchType,
  searchTypeIsSupported: supported,
} = storeToRefs(searchStore)

const results = computed(() => {
  const st = searchType.value
  return st === ALL_MEDIA
    ? mediaStore.allMedia
    : isSupportedMediaType(st)
    ? mediaStore.resultItems[st]
    : []
})

const { fetchState } = storeToRefs(mediaStore)

const isAllView = computed(() => searchType.value === ALL_MEDIA)

const pageTitle = ref(`${searchTerm.value} | Openverse`)
watch(searchTerm, (newTerm) => {
  pageTitle.value = `${newTerm} | Openverse`
})
</script>
