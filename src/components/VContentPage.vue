<template>
  <div class="pt-5 md:pt-10" dir="ltr">
    <div
      class="px-6 lg:px-0 mb-10 lg:mb-30 md:max-w-4xl xl:max-w-5xl prose prose-sm md:prose-base mx-auto max-w-none prose-headings:font-bold lg:prose-headings:text-3xl prose-h1:text-4xl prose-h1:text-bold lg:prose-h1:text-6xl md:prose-h1:mb-10 prose-h3:text-2xl prose-h3:font-semibold md:prose-h3:mt-10"
    >
      <slot default />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

export default defineComponent({
  name: 'VContentPage',
})
</script>
