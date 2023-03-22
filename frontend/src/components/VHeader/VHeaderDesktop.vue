<template>
  <header
    class="main-header z-30 flex w-full items-stretch justify-between gap-x-2 border-b bg-white py-4 px-6"
    :class="
      isHeaderScrolled || isSidebarVisible
        ? 'border-dark-charcoal-20'
        : 'border-white'
    "
  >
    <VLogoButton :is-fetching="isFetching" class="h-12" />

    <VSearchBar
      ref="searchBarRef"
      v-model.trim="searchTerm"
      class="flex-grow me-4"
      size="medium"
      @submit="handleSearch"
    >
      <VSearchBarButton
        v-show="searchTerm !== ''"
        :icon-path="closeIcon"
        :aria-label="$t('browse-page.search-form.clear')"
        inner-area-classes="bg-white hover:bg-dark-charcoal-10"
        class="hidden group-focus-within:flex"
        @click="clearSearchTerm"
      />
      <span
        v-show="Boolean(searchStatus)"
        class="info mx-4 hidden whitespace-nowrap text-xs text-dark-charcoal-70 group-focus-within:hidden group-hover:text-dark-charcoal group-focus:text-dark-charcoal lg:block"
      >
        {{ searchStatus }}
      </span>
    </VSearchBar>

    <VSearchTypePopover :show-label="isXl" placement="header" />

    <VFilterButton
      ref="filterButtonRef"
      class="flex self-stretch"
      :pressed="isSidebarVisible"
      :disabled="areFiltersDisabled"
      aria-haspopup="dialog"
      :aria-expanded="isSidebarVisible"
      @toggle="toggleSidebar"
    />
  </header>
</template>
<script lang="ts">
import { computed, defineComponent, inject, ref } from "vue"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { IsHeaderScrolledKey, IsSidebarVisibleKey } from "~/types/provides"

import { useSearch } from "~/composables/use-search"

import { ensureFocus } from "~/utils/reakit-utils/focus"

import VFilterButton from "~/components/VHeader/VFilterButton.vue"
import VSearchBar from "~/components/VHeader/VSearchBar/VSearchBar.vue"
import VLogoButton from "~/components/VHeader/VLogoButton.vue"
import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"
import VSearchTypePopover from "~/components/VContentSwitcher/VSearchTypePopover.vue"

import closeIcon from "~/assets/icons/close-small.svg"

/**
 * The desktop search header.
 */
export default defineComponent({
  name: "VHeaderDesktop",
  components: {
    VFilterButton,
    VLogoButton,
    VSearchBarButton,
    VSearchTypePopover,
    VSearchBar,
  },
  setup() {
    const filterButtonRef = ref<InstanceType<typeof VFilterButton> | null>(null)
    const searchBarRef = ref<InstanceType<typeof VSearchBar> | null>(null)

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const uiStore = useUiStore()

    const isHeaderScrolled = inject(IsHeaderScrolledKey)
    const isSidebarVisible = inject(IsSidebarVisibleKey)

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const { updateSearchState, searchTerm, searchStatus } = useSearch()

    const clearSearchTerm = () => {
      searchTerm.value = ""
      ensureFocus(searchBarRef.value?.$el.querySelector("input") as HTMLElement)
    }

    const handleSearch = async () => {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" })

      document.activeElement?.blur()
      updateSearchState()
    }
    const areFiltersDisabled = computed(
      () => !searchStore.searchTypeIsSupported
    )

    const toggleSidebar = () => uiStore.toggleFilters()

    const isXl = computed(() => uiStore.isBreakpoint("xl"))

    return {
      closeIcon,
      filterButtonRef,
      searchBarRef,
      isFetching,

      isHeaderScrolled,
      isSidebarVisible,
      areFiltersDisabled,
      isXl,

      handleSearch,
      clearSearchTerm,
      searchStatus,
      searchTerm,
      toggleSidebar,
    }
  },
})
</script>
