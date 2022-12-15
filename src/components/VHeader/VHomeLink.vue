<template>
  <VLink
    href="/"
    class="flex items-stretch rounded-sm focus-visible:outline-none focus-visible:ring focus-visible:ring-pink focus-visible:ring-offset-1 focus-visible:ring-offset-tx"
    :class="variant === 'dark' ? 'text-dark-charcoal' : 'text-white'"
  >
    <VBrand :is-fetching="false" :sr-text="$t('header.home-link').toString()" />
  </VLink>
</template>

<script lang="ts">
import { type PropType, defineComponent } from "@nuxtjs/composition-api"

import VBrand from "~/components/VBrand/VBrand.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VHomeLink",
  components: {
    VBrand,
    VLink,
  },
  props: {
    /**
     * In `light` mode, the links are white and the background is dark charcoal.
     * In `dark` mode, the links are dark charcoal and the background is transparent.
     *
     * @default 'light'
     */
    variant: {
      type: String as PropType<"light" | "dark">,
      default: "light",
    },
  },
})
</script>
