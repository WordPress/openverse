<script setup lang="ts">
import { computed, onMounted, provide, ref, watch } from "vue"
import { useScroll } from "@vueuse/core"

import { useUiStore } from "~/stores/ui"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"

import { IsHeaderScrolledKey, IsSidebarVisibleKey } from "~/types/provides"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"
import VSafeBrowsing from "~/components/VSafeBrowsing/VSafeBrowsing.vue"
import VHeaderDesktop from "~/components/VHeader/VHeaderDesktop.vue"
import VHeaderMobile from "~/components/VHeader/VHeaderMobile/VHeaderMobile.vue"

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
let mainPageElement = ref<HTMLElement | null>(null)

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

const headerBorder = computed(() =>
  isHeaderScrolled.value || isSidebarVisible.value
    ? "border-b-default"
    : "border-b-tx"
)
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
    <div class="header-el bg-default">
      <VBanners />
      <VHeaderDesktop
        v-if="isDesktopLayout"
        class="h-20 border-b bg-default"
        :class="headerBorder"
      />
      <VHeaderMobile
        v-else
        class="h-20 border-b bg-default"
        :class="headerBorder"
      />
    </div>

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
  </div>
</template>

<style scoped>
.has-sidebar .sidebar {
  width: var(--filter-sidebar-width);
}
.app {
  grid-template-areas: "header" "main";
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
