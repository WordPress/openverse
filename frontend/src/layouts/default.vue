<template>
  <div>
    <VSkipToContentButton />
    <div
      class="app h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] flex-col bg-yellow"
      :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]"
    >
      <div class="header-el">
        <VBanners />
        <VHeaderInternal class="bg-yellow" />
      </div>
      <div class="main-content flex flex-grow flex-col overflow-y-scroll">
        <Nuxt class="flex-grow" />
        <VFooter mode="internal" class="bg-yellow" />
      </div>
    </div>
    <VModalTarget class="modal" />
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, onMounted } from "vue"

import { useLayout } from "~/composables/use-layout"

import { useUiStore } from "~/stores/ui"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"
import VSkipToContentButton from "~/components/VSkipToContentButton.vue"

/**
 * The default layout is one screen high and yellow, without sidebars.
 */
export default defineComponent({
  name: "DefaultLayout",
  components: {
    VSkipToContentButton,
    VBanners,
    VFooter,
    VHeaderInternal,
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

    return {
      isDesktopLayout,
      breakpoint,
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
.main-content {
  grid-area: main;
}
</style>
