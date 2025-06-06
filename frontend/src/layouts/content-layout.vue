<script setup lang="ts">
import { computed, provide, ref, watch } from "vue"

import { useWindowScroll } from "@vueuse/core"

import { ShowScrollButtonKey } from "#shared/types/provides"

import VFooter from "~/components/VFooter/VFooter.vue"
import VHeader from "~/components/VHeader/VHeader.vue"
import VScrollButton from "~/components/VScrollButton.vue"

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
  <div
    class="app min-h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] bg-default"
  >
    <VHeader
      kind="internal"
      :show-bottom-border="isHeaderScrolled"
      class="header-el sticky top-0 z-40"
    />

    <div class="main-page flex h-full w-full min-w-0 flex-col justify-between">
      <slot />
      <VFooter mode="internal" class="border-t border-default bg-default" />
    </div>

    <VScrollButton
      v-show="showScrollButton"
      :is-filter-sidebar-visible="false"
      data-testid="scroll-button"
    />
  </div>
</template>

<style scoped>
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
</style>
