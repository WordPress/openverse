<script setup lang="ts">
import { skipToContentTargetId } from "#shared/constants/window"
</script>

<template>
  <main
    :id="skipToContentTargetId"
    tabindex="-1"
    class="grow pt-5 md:pt-10"
    dir="ltr"
  >
    <div
      class="prose-h1:text-bold mx-auto prose-sm mb-10 max-w-none px-6 md:prose-base md:max-w-4xl lg:mb-30 lg:px-0 xl:max-w-5xl dark:text-secondary prose-headings:font-bold prose-headings:text-default lg:prose-headings:text-3xl prose-h1:text-4xl md:prose-h1:mb-10 lg:prose-h1:text-6xl prose-h2:text-2xl prose-h2:font-semibold md:prose-h2:mt-10 prose-h3:text-2xl prose-h3:font-semibold md:prose-h3:mt-10 prose-a:font-medium"
    >
      <slot default />
    </div>
  </main>
</template>
