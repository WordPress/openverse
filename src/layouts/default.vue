<template>
  <div
    class="app flex min-h-screen flex-col"
    :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]"
  >
    <div class="sticky top-0 z-40 block">
      <VTeleportTarget name="skip-to-content" :force-destroy="true" />
      <VBanners />
      <template v-if="isNewHeaderEnabled">
        <template v-if="isSearchHeader">
          <VHeaderDesktop v-if="isDesktopLayout" />
          <VHeaderMobile v-else />
        </template>
        <VHeaderInternal
          v-else
          class="bg-white"
          :class="{ 'border-b-dark-charcoal-20': isHeaderScrolled }"
        />
      </template>
      <VHeaderOld v-else />
    </div>

    <main
      class="main embedded w-full flex-shrink-0 flex-grow md:w-full"
      :class="[
        { 'has-sidebar': isSidebarVisible },
        isNewHeaderEnabled ? 'new-layout' : 'old-layout',
      ]"
    >
      <div v-if="isNewHeaderEnabled" class="main-page min-w-0">
        <Nuxt />
        <VFooter
          :mode="isSearchHeader ? 'content' : 'search'"
          class="border-t border-dark-charcoal-20"
        />
      </div>
      <Nuxt v-else class="main-page min-w-0" />

      <aside
        v-if="isSidebarVisible"
        class="sidebar fixed z-10 overflow-y-auto bg-dark-charcoal-06 end-0"
        :class="{ 'border-dark-charcoal-20 border-s': isSidebarVisible }"
      >
        <VSearchGridFilter class="px-10 pt-8 pb-10" @close="closeSidebar" />
      </aside>
    </main>

    <VModalTarget class="modal" />
    <VGlobalAudioSection />
  </div>
</template>
<script lang="ts">
import {
  computed,
  onMounted,
  provide,
  ref,
  watch,
} from "@nuxtjs/composition-api"
import { PortalTarget as VTeleportTarget } from "portal-vue"

import { useWindowScroll } from "~/composables/use-window-scroll"
import {
  useMatchSearchRoutes,
  useMatchSingleResultRoutes,
} from "~/composables/use-match-routes"
import { useLayout } from "~/composables/use-layout"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"
import { useSearchStore } from "~/stores/search"

import { IsHeaderScrolledKey, IsSidebarVisibleKey } from "~/types/provides"

import VBanners from "~/components/VBanner/VBanners.vue"
import VHeaderOld from "~/components/VHeaderOld/VHeaderOld.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"
import VGlobalAudioSection from "~/components/VGlobalAudioSection/VGlobalAudioSection.vue"
import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"

const embeddedPage = {
  name: "embedded",
  components: {
    VBanners,
    VHeaderDesktop: () => import("~/components/VHeader/VHeaderDesktop.vue"),
    VHeaderInternal: () => import("~/components/VHeader/VHeaderInternal.vue"),
    VHeaderMobile: () =>
      import("~/components/VHeader/VHeaderMobile/VHeaderMobile.vue"),
    VFooter: () => import("~/components/VFooter/VFooter.vue"),
    VHeaderOld,
    VModalTarget,
    VTeleportTarget,
    VGlobalAudioSection,
    VSearchGridFilter,
  },
  layout: "embedded",
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
  setup() {
    const uiStore = useUiStore()
    const featureFlagStore = useFeatureFlagStore()
    const searchStore = useSearchStore()

    const isNewHeaderEnabled = computed(() =>
      featureFlagStore.isOn("new_header")
    )
    const { updateBreakpoint } = useLayout()

    /**
     * Update the breakpoint value in the cookie on mounted.
     * The Pinia state might become different from the cookie state if, for example, the cookies were saved when the screen was `sm`,
     * and then a page is opened on SSR on a `lg` screen.
     */
    onMounted(() => {
      updateBreakpoint()
    })

    const { matches: isSearchRoute } = useMatchSearchRoutes()
    const { matches: isSingleResultRoute } = useMatchSingleResultRoutes()
    const isSearchHeader = computed(
      () => isSearchRoute.value || isSingleResultRoute.value
    )

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)

    /**
     * Filters sidebar is visible only on desktop layouts
     * on search result pages for supported search types.
     */
    const isSidebarVisible = computed(
      () =>
        isSearchRoute.value &&
        searchStore.searchTypeIsSupported &&
        uiStore.isFilterVisible &&
        isDesktopLayout.value
    )

    const closeSidebar = () => {
      uiStore.setFiltersState(false)
    }

    const isHeaderScrolled = ref(false)
    const { isScrolled: isMainContentScrolled, y: scrollY } = useWindowScroll()
    watch([isMainContentScrolled], ([isMainContentScrolled]) => {
      isHeaderScrolled.value = isMainContentScrolled
    })
    const showScrollButton = computed(() => scrollY.value > 70)

    provide("isHeaderScrolled", isHeaderScrolled)
    provide("showScrollButton", showScrollButton)
    provide(IsHeaderScrolledKey, isHeaderScrolled)
    provide(IsSidebarVisibleKey, isSidebarVisible)

    // TODO: remove `headerHasTwoRows` provide after the new header is enabled.
    const headerHasTwoRows = computed(
      () =>
        isSearchRoute.value && !isHeaderScrolled.value && !isDesktopLayout.value
    )
    provide("headerHasTwoRows", headerHasTwoRows)

    return {
      isHeaderScrolled,
      isDesktopLayout,
      isSidebarVisible,
      isSearchRoute,
      isSearchHeader,
      headerHasTwoRows,
      isNewHeaderEnabled,
      breakpoint: computed(() => uiStore.breakpoint),

      closeSidebar,
    }
  },
}
export default embeddedPage
</script>

<style scoped>
.sidebar {
  /* Header height above md is 80px plus 1px for bottom border */
  height: calc(100vh - 81px);
}
.has-sidebar .sidebar {
  width: var(--filter-sidebar-width);
}

/* TODO: remove these styles when new header is enabled */
@screen md {
  /** Display the search filter sidebar and results as independently-scrolling. **/
  .main.old-layout {
    @apply grid h-full grid-cols-[1fr_var(--filter-sidebar-width)];
  }
  /** Make the main content area span both grid columns when the sidebar is closed... **/
  .main.old-layout > *:first-child {
    grid-column: span 2;
  }
  /** ...and only one column when it is visible. **/
  .main.old-layout.has-sidebar > *:first-child {
    grid-column: 1;
  }
}
/* TODO: remove the new-layout class when new header is enabled */
@screen lg {
  /** Display the search filter sidebar and results as independently-scrolling. **/
  .main.new-layout {
    @apply grid h-full grid-cols-[1fr_var(--filter-sidebar-width)];
  }
  /** Make the main content area span both grid columns when the sidebar is closed... **/
  .main.new-layout > *:first-child {
    grid-column: span 2;
    /** Make sure the bottom element (footer) is all the way at the bottom of the page **/
    @apply flex flex-col justify-between;
  }
  /** ...and only one column when it is visible. **/
  .main.new-layout.has-sidebar > *:first-child {
    grid-column: 1;
  }
}
</style>
