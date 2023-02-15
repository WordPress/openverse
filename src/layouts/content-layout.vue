<template>
  <div
    class="app flex min-h-screen min-h-[100dvh] flex-col bg-white"
    :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]"
  >
    <div class="sticky top-0 z-40 block">
      <VTeleportTarget name="skip-to-content" :force-destroy="true" />
      <VBanners />
      <template v-if="isSearchHeader">
        <VHeaderDesktop v-if="isDesktopLayout" class="bg-white" />
        <VHeaderMobile v-else class="bg-white" />
      </template>
      <VHeaderInternal
        v-else
        class="bg-white"
        :class="{ 'border-b-dark-charcoal-20': isHeaderScrolled }"
      />
    </div>

    <main
      class="main grid h-full flex-grow"
      :class="[
        { 'has-sidebar': isSidebarVisible },
        isSidebarVisible
          ? 'grid-cols-[1fr_var(--filter-sidebar-width)]'
          : 'grid-cols-1',
      ]"
    >
      <div
        class="main-page flex h-full w-full min-w-0 flex-col justify-between"
      >
        <Nuxt />
        <VFooter
          :mode="isSearchHeader ? 'content' : 'search'"
          class="border-t border-dark-charcoal-20 bg-white"
        />
      </div>

      <aside
        v-if="isSidebarVisible"
        class="sidebar fixed z-10 h-[calc(100vh-81px)] h-[calc(100dvh-81px)] overflow-y-auto border-dark-charcoal-20 bg-dark-charcoal-06 end-0 border-s"
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
  defineComponent,
  onMounted,
  provide,
  ref,
  useContext,
  watch,
} from "@nuxtjs/composition-api"
import { PortalTarget as VTeleportTarget } from "portal-vue"

import { useWindowScroll } from "~/composables/use-window-scroll"
import {
  useMatchSearchRoutes,
  useMatchSingleResultRoutes,
} from "~/composables/use-match-routes"
import { useLayout } from "~/composables/use-layout"

import { useUiStore } from "~/stores/ui"
import { useSearchStore } from "~/stores/search"

import { IsHeaderScrolledKey, IsSidebarVisibleKey } from "~/types/provides"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"
import VGlobalAudioSection from "~/components/VGlobalAudioSection/VGlobalAudioSection.vue"
import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"

/**
 * This is the ContentLayout: the search page, the single result page,
 * and the content pages.
 * It has white background and is scrollable. It can also have a sidebar.
 */
export default defineComponent({
  name: "ContentLayout",
  components: {
    VBanners,
    VHeaderDesktop: () => import("~/components/VHeader/VHeaderDesktop.vue"),
    VHeaderInternal: () => import("~/components/VHeader/VHeaderInternal.vue"),
    VHeaderMobile: () =>
      import("~/components/VHeader/VHeaderMobile/VHeaderMobile.vue"),
    VFooter,
    VModalTarget,
    VTeleportTarget,
    VGlobalAudioSection,
    VSearchGridFilter,
  },
  setup() {
    const { app } = useContext()
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

    const { matches: isSearchRoute } = useMatchSearchRoutes()
    const { matches: isSingleResultRoute } = useMatchSingleResultRoutes()

    const nuxtError = computed(() => app.nuxt.err)

    const isSearchHeader = computed(
      () =>
        !nuxtError.value && (isSearchRoute.value || isSingleResultRoute.value)
    )

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
    const breakpoint = computed(() => uiStore.breakpoint)

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

    return {
      isHeaderScrolled,
      isDesktopLayout,
      isSidebarVisible,
      isSearchRoute,
      isSearchHeader,
      breakpoint,

      closeSidebar,
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
</style>
