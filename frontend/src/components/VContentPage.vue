<template>
  <VSkipToContentContainer as="main" class="pt-5 md:pt-10" dir="ltr">
    <div
      class="prose-h1:text-bold prose prose-sm mx-auto mb-10 max-w-none px-6 prose-headings:font-bold prose-h1:text-4xl prose-h2:text-2xl prose-h2:font-semibold prose-h3:text-2xl prose-h3:font-semibold md:max-w-4xl md:prose-base md:prose-h1:mb-10 md:prose-h2:mt-10 md:prose-h3:mt-10 lg:mb-30 lg:px-0 lg:prose-headings:text-3xl lg:prose-h1:text-6xl xl:max-w-5xl"
    >
      <slot default />
    </div>
  </VSkipToContentContainer>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api"

export default defineComponent({
  name: "VContentPage",
})
</script>
