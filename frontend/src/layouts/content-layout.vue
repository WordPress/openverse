<script setup lang="ts">
import { computed, provide, ref, watch } from "vue"

import { useWindowScroll } from "@vueuse/core"

import { ShowScrollButtonKey } from "~/types/provides"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"

/**
 * This is the ContentLayout: the single result and the content pages.
 * It has white background and is scrollable.
 */
defineOptions({
  name: "ContentLayout",
})

const isHeaderScrolled = ref(false)
const { y: scrollY } = useWindowScroll()
const isMainContentScrolled = computed(() => scrollY.value > 0)
watch([isMainContentScrolled], ([isMainContentScrolled]) => {
  isHeaderScrolled.value = isMainContentScrolled
})
const showScrollButton = computed(() => scrollY.value > 70)

provide(ShowScrollButtonKey, showScrollButton)
</script>

<template>
  <div class="app min-h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] bg-bg">
    <div class="header-el sticky top-0 z-40 block bg-bg">
      <VBanners />
      <VHeaderInternal
        class="h-20 border-b bg-bg"
        :class="isHeaderScrolled ? 'border-b-border' : 'border-b-tx'"
      />
    </div>

    <div class="main-page flex h-full w-full min-w-0 flex-col justify-between">
      <slot />
      <VFooter mode="internal" class="border-t border-border bg-bg" />
    </div>
  </div>
</template>

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
