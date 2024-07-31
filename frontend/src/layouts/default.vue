<template>
  <div
    class="app h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] flex-col bg-yellow-3-3"
  >
    <div class="header-el">
      <VBanners />
      <VHeaderInternal class="bg-yellow-3-3" />
    </div>
    <div class="main-content flex flex-grow flex-col overflow-y-scroll">
      <slot class="flex-grow" />
      <VFooter mode="internal" class="bg-yellow-3-3" />
    </div>
  </div>
</template>
<script lang="ts">
import { defineComponent } from "vue"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"

/**
 * The default layout is one screen high and yellow-3-3, without sidebars.
 */
export default defineComponent({
  name: "DefaultLayout",
  components: {
    VBanners,
    VFooter,
    VHeaderInternal,
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
