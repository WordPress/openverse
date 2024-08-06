<template>
  <main
    :id="skipToContentTargetId"
    tabindex="-1"
    class="flex-grow pt-5 md:pt-10"
    dir="ltr"
  >
    <div
      class="prose-h1:text-bold prose-body:text-text prose-sm mx-auto mb-10 max-w-none px-6 text-text md:prose-base prose-headings:font-bold prose-headings:text-text prose-h1:text-4xl prose-h2:text-2xl prose-h2:font-semibold prose-h3:text-2xl prose-h3:font-semibold prose-a:font-medium md:max-w-4xl md:prose-h1:mb-10 md:prose-h2:mt-10 md:prose-h3:mt-10 lg:mb-30 lg:px-0 lg:prose-headings:text-3xl lg:prose-h1:text-6xl xl:max-w-5xl"
    >
      <slot default />
    </div>
  </main>
</template>

<script lang="ts">
import { defineComponent } from "vue"

import { skipToContentTargetId } from "~/constants/window"

export default defineComponent({
  name: "VContentPage",
  setup() {
    return {
      skipToContentTargetId,
    }
  },
})
</script>
