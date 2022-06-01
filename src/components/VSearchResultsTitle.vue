<template>
  <h1
    class="leading-tight sr-only md:not-sr-only break-words"
    :class="[size === 'large' ? 'text-[90px]' : 'text-6xl']"
  >
    <slot default />
  </h1>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

const sizes = {
  DEFAULT: 'default',
  LARGE: 'large',
}
export default defineComponent({
  name: 'VSearchResultsTitle',
  props: {
    size: {
      required: false,
      default: sizes.DEFAULT,
      validator: (value) => Object.values(sizes).includes(value),
    },
  },
})
</script>

<style scoped>
/* Title case the user's search query */
h1:first-letter {
  text-transform: uppercase;
}
</style>
