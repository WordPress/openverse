<template>
  <div class="relative">
    <VSkipToContentButton />
    <div
      class="app h-dyn-screen min-h-dyn-screen grid grid-rows-[auto,1fr] bg-white"
      :class="[
        isDesktopLayout ? 'desktop' : 'mobile',
        breakpoint,
        { 'has-sidebar': isSidebarVisible },
        isSidebarVisible
          ? 'grid-cols-[1fr_var(--filter-sidebar-width)]'
          : 'grid-cols-1',
      ]"
    >
      <div class="header-el bg-white">
        <VBanners />
        <VHeaderDesktop
          v-if="isDesktopLayout"
          class="h-20 border-b bg-white"
          :class="headerBorder"
        />
        <VHeaderMobile
          v-else
          class="h-20 border-b bg-white"
          :class="headerBorder"
        />
      </div>

      <aside
        v-if="isSidebarVisible"
        class="sidebar end-0 z-10 h-full overflow-y-auto border-s border-dark-charcoal-20 bg-dark-charcoal-06"
      >
        <VSearchGridFilter class="px-10 py-8" />
        <VSafeBrowsing class="border-t border-dark-charcoal-20 px-10 py-8" />
      </aside>

      <div
        id="main-page"
        class="main-page flex h-full w-full min-w-0 flex-col justify-between overflow-y-auto"
      >
        <Nuxt />
        <VFooter
          mode="content"
          class="border-t border-dark-charcoal-20 bg-white"
        />
      </div>
      <VGlobalAudioSection />
    </div>
    <VModalTarget class="modal" />
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, onMounted, provide, ref, watch } from "vue"
import { useScroll } from "@vueuse/core"

import { useLayout } from "~/composables/use-layout"

import { useUiStore } from "~/stores/ui"
import { useSearchStore } from "~/stores/search"

import {
  IsHeaderScrolledKey,
  IsSidebarVisibleKey,
  ShowScrollButtonKey,
} from "~/types/provides"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"
import VGlobalAudioSection from "~/components/VGlobalAudioSection/VGlobalAudioSection.vue"
import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"
import VSkipToContentButton from "~/components/VSkipToContentButton.vue"
import VSafeBrowsing from "~/components/VSafeBrowsing/VSafeBrowsing.vue"

/**
 * This is the SearchLayout: the search page that has a sidebar.
 * It has white background.
 */
export default defineComponent({
  name: "SearchLayout",
  components: {
    VSafeBrowsing,
    VSkipToContentButton,
    VBanners,
    VHeaderDesktop: () => import("~/components/VHeader/VHeaderDesktop.vue"),
    VHeaderMobile: () =>
      import("~/components/VHeader/VHeaderMobile/VHeaderMobile.vue"),
    VFooter,
    VModalTarget,
    VGlobalAudioSection,
    VSearchGridFilter,
  },
  setup() {
    const headerRef = ref<HTMLElement | null>(null)
    const mainPageRef = ref<HTMLElement | null>(null)

    const uiStore = useUiStore()
    const searchStore = useSearchStore()

    const { updateBreakpoint } = useLayout()

    /**
     * Update the breakpoint value in the cookie on mounted.
     * The Pinia state might become different from the cookie state if, for example, the cookies were saved when the screen was `sm`,
     * and then a page is opened on SSR on a `lg` screen.
     */
    onMounted(() => {
      updateBreakpoint()
    })

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
    const breakpoint = computed(() => uiStore.breakpoint)

    /**
     * Filters sidebar is visible only on desktop layouts
     * on search result pages for supported search types.
     */
    const isSidebarVisible = computed(
      () =>
        searchStore.searchTypeIsSupported &&
        uiStore.isFilterVisible &&
        isDesktopLayout.value
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

    provide(ShowScrollButtonKey, showScrollButton)
    provide(IsHeaderScrolledKey, isHeaderScrolled)
    provide(IsSidebarVisibleKey, isSidebarVisible)

    const headerBorder = computed(() =>
      isHeaderScrolled.value || isSidebarVisible.value
        ? "border-b-dark-charcoal-20"
        : "border-b-tx"
    )

    return {
      mainPageRef,
      headerRef,

      isHeaderScrolled,
      isDesktopLayout,
      isSidebarVisible,
      breakpoint,

      headerBorder,
    }
  },
  head() {
    return this.$nuxtI18nHead({
      addSeoAttributes: true,
      addDirAttribute: true,
    })
  },
})
</script>

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
