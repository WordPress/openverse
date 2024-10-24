<script setup lang="ts">
import { computed, onMounted, provide, ref, watch } from "vue"
import { useScroll } from "@vueuse/core"

import { useUiStore } from "~/stores/ui"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"

import {
  IsHeaderScrolledKey,
  IsSidebarVisibleKey,
  ShowScrollButtonKey,
} from "~/types/provides"

import VFooter from "~/components/VFooter/VFooter.vue"
import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"
import VSafeBrowsing from "~/components/VSafeBrowsing/VSafeBrowsing.vue"
import VHeader from "~/components/VHeader/VHeader.vue"
import VScrollButton from "~/components/VScrollButton.vue"

defineOptions({
  name: "SearchLayout",
})

/**
 * This is the SearchLayout: the search page that has a sidebar.
 * It has white background.
 */
const uiStore = useUiStore()
const searchStore = useSearchStore()

const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
const supported = computed(() => isSearchTypeSupported(searchStore.searchType))

/**
 * Filters sidebar is visible only on desktop layouts
 * on search result pages for supported search types.
 */
const isSidebarVisible = computed(
  () => supported.value && uiStore.isFilterVisible && isDesktopLayout.value
)

const isHeaderScrolled = ref(false)
const showScrollButton = ref(false)

/**
 * Update the `isHeaderScrolled` and `showScrollButton` values on `main-page` scroll.
 *
 * Note: template refs do not work in a Nuxt layout, so we get the `main-page` element using `document.getElementById`.
 */
const mainPageElement = ref<HTMLElement | null>(null)

const { y: mainPageY } = useScroll(mainPageElement)
watch(mainPageY, (y) => {
  isHeaderScrolled.value = y > 0
  showScrollButton.value = y > 70
})

onMounted(() => {
  mainPageElement.value = document.getElementById("main-page")
})

provide(IsHeaderScrolledKey, isHeaderScrolled)
provide(IsSidebarVisibleKey, isSidebarVisible)
provide(ShowScrollButtonKey, showScrollButton)
</script>

<template>
  <div
    class="app h-dyn-screen min-h-dyn-screen grid grid-rows-[auto,1fr] bg-default"
    :class="[
      isSidebarVisible
        ? 'has-sidebar grid-cols-[1fr_var(--filter-sidebar-width)]'
        : 'grid-cols-1',
    ]"
  >
    <VHeader
      class="header-el"
      :kind="isDesktopLayout ? 'search-desktop' : 'search-mobile'"
      :show-bottom-border="isHeaderScrolled || isSidebarVisible"
    />

    <aside
      v-if="isSidebarVisible"
      class="sidebar end-0 z-10 h-full overflow-y-auto border-s border-default bg-surface"
    >
      <VSearchGridFilter class="px-10 py-8" />
      <VSafeBrowsing class="border-t border-default px-10 py-8" />
    </aside>

    <div
      id="main-page"
      class="main-page flex h-full w-full min-w-0 flex-col justify-between overflow-y-auto"
    >
      <slot />
      <VFooter mode="content" class="border-t border-default bg-default" />
    </div>

    <VScrollButton
      v-show="showScrollButton"
      :is-filter-sidebar-visible="isSidebarVisible"
      data-testid="scroll-button"
    />
  </div>
</template>

<style scoped>
.has-sidebar .sidebar {
  width: var(--filter-sidebar-width);
}
.app {
  grid-template-areas: "header" "main";
  /* This is used by some elements. */
  --color-bg-curr-page: var(--color-bg);
}
.header-el {
  grid-area: header;
}
.main-page {
  grid-area: main;
}
.sidebar {
  grid-area: sidebar;
}
.has-sidebar.app {
  grid-template-areas: "header header" "main sidebar";
}
</style>
