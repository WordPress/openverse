<template>
  <VButton
    type="submit"
    :aria-label="$t('search.search')"
    size="disabled"
    variant="plain"
    :class="[
      'h-full flex-shrink-0 rounded-s-none border-s-0 p-0.5px ps-1.5px focus-slim-filled hover:text-white focus-visible:border-s group-focus-within:border-tx group-focus-within:bg-pink group-focus-within:text-white group-focus-within:hover:bg-dark-pink group-hover:border-tx group-hover:bg-pink group-hover:text-white',
      route === 'search' ? 'w-12' : 'w-14 sm:w-16',
      {
        'border-tx bg-dark-charcoal-10 hover:bg-pink ': route === 'search',
        'border-tx bg-pink text-white hover:!bg-dark-pink': route === 'home',
      },
    ]"
  >
    <VIcon name="search" />
  </VButton>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"
/**
 * The search button used in the search bar on the home, 404 and search pages.
 */
export default defineComponent({
  name: "VSearchButton",
  components: { VIcon, VButton },
  props: {
    /**
     * The current route determines the size and the style of the button.
     */
    route: {
      type: String as PropType<"home" | "404" | "search">,
      required: true,
    },
  },
})
</script>
