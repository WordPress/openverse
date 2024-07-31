<template>
  <VButton
    type="submit"
    :aria-label="$t('search.search')"
    size="disabled"
    :disabled="!doneHydrating"
    variant="plain"
    :class="[
      'focus-slim-filled h-full flex-shrink-0 rounded-s-none border-s-0 p-0.5px ps-1.5px hover:text-white focus-visible:border-s group-focus-within:border-tx group-focus-within:bg-pink-8 group-focus-within:text-white group-focus-within:hover:bg-pink-9 group-hover:border-tx group-hover:bg-pink-8 group-hover:text-white',
      route === 'search' ? 'w-12' : 'w-14 sm:w-16',
      {
        'border-tx bg-gray-2 hover:bg-pink-8': route === 'search',
        'border-tx bg-pink-8 text-white hover:!bg-pink-9': route === 'home',
      },
    ]"
  >
    <VIcon name="search" />
  </VButton>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import { useHydrating } from "~/composables/use-hydrating"

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
  setup() {
    const { doneHydrating } = useHydrating()

    return {
      doneHydrating,
    }
  },
})
</script>
