<template>
  <div
    class="app min-h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] bg-white"
  >
    <div class="header-el sticky top-0 z-40 block bg-white">
      <VBanners />
      <VHeaderInternal
        class="h-20 border-b bg-white"
        :class="isHeaderScrolled ? 'border-b-gray-3' : 'border-b-tx'"
      />
    </div>

    <div class="main-page flex h-full w-full min-w-0 flex-col justify-between">
      <slot />
      <VFooter mode="internal" class="border-gray-3 border-t bg-white" />
    </div>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent, provide, ref, watch } from "vue"

import { useWindowScroll } from "@vueuse/core"

import { useUiStore } from "~/stores/ui"

import { ShowScrollButtonKey } from "~/types/provides"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"

/**
 * This is the ContentLayout: the search page, the single result page,
 * and the content pages.
 * It has white background and is scrollable.
 */
export default defineComponent({
  name: "ContentLayout",
  components: {
    VBanners,
    VFooter,
    VHeaderInternal,
  },
  setup() {
    const uiStore = useUiStore()
    const closeSidebar = () => {
      uiStore.setFiltersState(false)
    }

    const isHeaderScrolled = ref(false)
    const { y: scrollY } = useWindowScroll()
    const isMainContentScrolled = computed(() => scrollY.value > 0)
    watch([isMainContentScrolled], ([isMainContentScrolled]) => {
      isHeaderScrolled.value = isMainContentScrolled
    })
    const showScrollButton = computed(() => scrollY.value > 70)

    provide(ShowScrollButtonKey, showScrollButton)

    return {
      isHeaderScrolled,

      closeSidebar,
    }
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
