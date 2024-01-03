<template>
  <div
    class="app h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] flex-col bg-yellow"
  >
    <div class="header-el">
      <VBanners />
      <VHeaderInternal class="bg-yellow" />
    </div>
    <div class="main-content flex flex-grow flex-col overflow-y-scroll">
      <slot class="flex-grow" />
      <VFooter mode="internal" class="bg-yellow" />
    </div>

    <VGlobalAudioSection />
  </div>
</template>
<script lang="ts">
import { defineComponent } from "vue"

import VBanners from "~/components/VBanner/VBanners.vue"
import VFooter from "~/components/VFooter/VFooter.vue"
import VGlobalAudioSection from "~/components/VGlobalAudioSection/VGlobalAudioSection.vue"
import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"

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
