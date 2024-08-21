<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed, inject, ref } from "vue"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { IsSidebarVisibleKey } from "~/types/provides"

import { useSearch } from "~/composables/use-search"
import { useHydrating } from "~/composables/use-hydrating"

import { ensureFocus } from "~/utils/reakit-utils/focus"

import VFilterButton from "~/components/VHeader/VFilterButton.vue"
import VSearchBar from "~/components/VHeader/VSearchBar/VSearchBar.vue"
import VLogoButton from "~/components/VHeader/VLogoButton.vue"
import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"
import VSearchTypePopover from "~/components/VContentSwitcher/VSearchTypePopover.vue"

import type { Ref } from "vue"

/**
 * The desktop search header.
 */

const filterButtonRef = ref<InstanceType<typeof VFilterButton> | null>(null)
const searchBarRef = ref<InstanceType<typeof VSearchBar> | null>(null)

const mediaStore = useMediaStore()
const searchStore = useSearchStore()
const uiStore = useUiStore()

const isSidebarVisible = inject<Ref<boolean>>(IsSidebarVisibleKey)

const isFetching = computed(() => mediaStore.fetchState.isFetching)

const { $sendCustomEvent } = useNuxtApp()

const { updateSearchState, searchTerm, searchStatus } =
  useSearch($sendCustomEvent)

const clearSearchTerm = () => {
  searchTerm.value = ""
  ensureFocus(searchBarRef.value?.$el.querySelector("input") as HTMLElement)
}

const handleSearch = async () => {
  window.scrollTo({ top: 0, left: 0, behavior: "auto" })
  const activeElement = document.activeElement as HTMLElement
  activeElement?.blur()
  updateSearchState()
}

const areFiltersDisabled = computed(() => !searchStore.searchTypeIsSupported)

const toggleSidebar = () => {
  const toState = isSidebarVisible?.value ? "closed" : "opened"
  $sendCustomEvent("TOGGLE_FILTER_SIDEBAR", {
    searchType: searchStore.searchType,
    toState,
  })
  uiStore.toggleFilters()
}

const isXl = computed(() => uiStore.isBreakpoint("xl"))

const { doneHydrating } = useHydrating()
</script>

<template>
  <header
    class="main-header z-30 flex w-full items-stretch justify-between gap-x-2 bg-default px-6 py-4"
  >
    <VLogoButton :is-fetching="isFetching" />

    <VSearchBar
      ref="searchBarRef"
      v-model.trim="searchTerm"
      class="me-4 flex-grow"
      @submit="handleSearch"
      @recent-hidden="handleSearch"
    >
      <VSearchBarButton
        v-show="searchTerm !== ''"
        icon="close-small"
        :label="$t('browsePage.searchForm.clear')"
        variant="filled-white"
        class="hidden group-focus-within:flex"
        @click="clearSearchTerm"
      />
      <span
        v-show="Boolean(searchStatus)"
        class="info mx-4 hidden whitespace-nowrap text-xs text-secondary group-focus-within:hidden group-hover:text-default group-focus:text-default lg:block"
      >
        {{ searchStatus }}
      </span>
    </VSearchBar>

    <VSearchTypePopover :show-label="isXl" placement="header" />

    <VFilterButton
      ref="filterButtonRef"
      class="flex self-stretch"
      :pressed="isSidebarVisible"
      :disabled="!doneHydrating || areFiltersDisabled"
      aria-haspopup="dialog"
      :aria-expanded="isSidebarVisible"
      @toggle="toggleSidebar"
    />
  </header>
</template>
