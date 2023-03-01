<template>
  <div
    class="app flex h-screen h-[100dvh] flex-col bg-yellow"
    :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]"
  >
    <div class="sticky top-0 z-40 block">
      <VTeleportTarget name="skip-to-content" :force-destroy="true" />
      <VBanners />
      <VHeaderInternal class="bg-yellow" />
    </div>
    <Nuxt class="flex-grow" />
    <VFooter mode="search" class="bg-yellow" />

    <VModalTarget class="modal" />
    <VGlobalAudioSection />
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, onMounted } from "vue"
import { PortalTarget as VTeleportTarget } from "portal-vue"

import { useLayout } from "~/composables/use-layout"

import { useUiStore } from "~/stores/ui"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VGlobalAudioSection from "~/components/VGlobalAudioSection/VGlobalAudioSection.vue"
import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"

/**
 * The default layout is one screen high and yellow, without sidebars.
 */
export default defineComponent({
  name: "DefaultLayout",
  components: {
    VBanners,
    VFooter,
    VGlobalAudioSection,
    VHeaderInternal,
    VModalTarget,
    VTeleportTarget,
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
