<template>
  <div class="relative">
    <VSkipToContentButton />
    <div
      class="app min-h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] bg-white"
      :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]"
    >
      <div class="header-el sticky top-0 z-40 block bg-white">
        <VBanners />
        <VHeaderInternal
          class="h-20 border-b bg-white"
          :class="
            isHeaderScrolled ? 'border-b-dark-charcoal-20' : 'border-b-tx'
          "
        />
      </div>

      <div
        class="main-page flex h-full w-full min-w-0 flex-col justify-between"
      >
        <Nuxt />
        <VFooter
          mode="internal"
          class="border-t border-dark-charcoal-20 bg-white"
        />
        <VGlobalAudioSection />
      </div>
    </div>
    <VModalTarget class="modal" />
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, onMounted, provide, ref, watch } from "vue"

import { useWindowScroll } from "~/composables/use-window-scroll"
import { useLayout } from "~/composables/use-layout"

import { useUiStore } from "~/stores/ui"

import { ShowScrollButtonKey } from "~/types/provides"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"
import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"
import VSkipToContentButton from "~/components/VSkipToContentButton.vue"
import VGlobalAudioSection from "~/components/VGlobalAudioSection/VGlobalAudioSection.vue"

/**
 * This is the ContentLayout: the search page, the single result page,
 * and the content pages.
 * It has white background and is scrollable. It can also have a sidebar.
 */
export default defineComponent({
  name: "ContentLayout",
  components: {
    VGlobalAudioSection,
    VSkipToContentButton,
    VBanners,
    VHeaderInternal,
    VFooter,
    VModalTarget,
  },
  setup() {
    const uiStore = useUiStore()

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

    const closeSidebar = () => {
      uiStore.setFiltersState(false)
    }

    const isHeaderScrolled = ref(false)
    const { isScrolled: isMainContentScrolled, y: scrollY } = useWindowScroll()
    watch([isMainContentScrolled], ([isMainContentScrolled]) => {
      isHeaderScrolled.value = isMainContentScrolled
    })
    const showScrollButton = computed(() => scrollY.value > 70)

    provide(ShowScrollButtonKey, showScrollButton)

    return {
      isHeaderScrolled,
      isDesktopLayout,
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
.app {
  grid-template-areas: "header" "main";
}
.header-el {
  grid-area: header;
}
.main-page {
  grid-area: main;
}
</style>
