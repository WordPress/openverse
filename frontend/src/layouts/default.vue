<script setup lang="ts">
import VFooter from "~/components/VFooter/VFooter.vue"
import VHeader from "~/components/VHeader/VHeader.vue"
/**
 * The default layout is one screen high and yellow, without sidebars.
 */
defineOptions({
  name: "DefaultLayout",
})
</script>

<template>
  <div
    class="app h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] flex-col bg-complementary"
  >
    <VHeader class="header-el" kind="internal" color="complementary" />
    <div class="main-content flex flex-grow flex-col overflow-y-scroll">
      <slot class="flex-grow" />
      <VFooter mode="internal" class="bg-complementary" />
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
.main-content {
  grid-area: main;
}
</style>
