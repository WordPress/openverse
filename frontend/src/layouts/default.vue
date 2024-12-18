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
    class="app h-dyn-screen grid grid-cols-1 grid-rows-[auto,1fr] flex-col bg-complementary dark:bg-default"
  >
    <VHeader class="header-el" kind="internal" color="complementary" />
    <div class="main-content flex flex-grow flex-col overflow-y-auto">
      <slot class="flex-grow" />
      <VFooter mode="internal" class="bg-complementary dark:bg-default" />
    </div>
  </div>
</template>

<style scoped>
.app {
  grid-template-areas: "header" "main";
  /* This is used by some elements. */
  --color-bg-curr-page: var(--color-bg-complementary);
}
@media (prefers-color-scheme: dark) {
  .app {
    --color-bg-curr-page: var(--color-bg);
  }
}
.header-el {
  grid-area: header;
}
.main-content {
  grid-area: main;
}
</style>
