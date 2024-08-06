<template>
  <VButton
    type="submit"
    :aria-label="$t('search.search')"
    size="disabled"
    :disabled="!doneHydrating"
    variant="plain"
    :class="[
      'h-full flex-shrink-0 rounded-s-none border-s-0 p-0.5px ps-1.5px focus-slim-filled hover:text-text-over-dark focus-visible:border-s group-focus-within:border-tx group-focus-within:bg-bg-fill-primary group-focus-within:text-text-over-dark group-focus-within:hover:bg-bg-fill-primary-hover group-hover:border-tx group-hover:bg-bg-fill-primary group-hover:text-text-over-dark',
      route === 'search' ? 'w-12' : 'w-14 sm:w-16',
      {
        'border-tx bg-bg-fill-secondary hover:bg-bg-fill-primary':
          route === 'search',
        'border-tx bg-bg-fill-primary text-text-over-dark hover:!bg-bg-fill-primary-hover':
          route === 'home',
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
