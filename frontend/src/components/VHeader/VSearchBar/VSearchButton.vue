<script setup lang="ts">
import { useHydrating } from "~/composables/use-hydrating"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"
/**
 * The search button used in the search bar on the home, 404 and search pages.
 */
defineProps<{
  /**
   * The current route determines the size and the style of the button.
   */
  route: "home" | "404" | "search"
}>()

const { doneHydrating } = useHydrating()
</script>

<template>
  <VButton
    type="submit"
    :aria-label="$t('search.search')"
    size="disabled"
    :disabled="!doneHydrating"
    variant="plain--avoid"
    :class="[
      'h-full flex-shrink-0 rounded-s-none border-1.5 p-0.5px hover:text-over-dark focus-visible:rounded-sm focus-visible:border-default focus-visible:ring focus-visible:ring-inset focus-visible:ring-[--color-bg] group-focus-within:border-tx group-focus-within:bg-primary group-focus-within:text-over-dark group-focus-within:hover:bg-primary-hover group-hover:border-tx group-hover:bg-primary group-hover:text-over-dark dark:focus-visible:ring-[--color-bg-overlay]',
      route === 'search' ? 'w-12' : 'w-14 sm:w-16',
      {
        'border-tx bg-secondary hover:bg-primary': route === 'search',
        'border-tx bg-primary text-over-dark hover:!bg-primary-hover':
          route === 'home',
        'border-s-0 border-black hover:border-s-1.5 focus-visible:border-s-1.5 group-focus-within:border-s-1.5 dark:border-tx':
          route === '404',
      },
    ]"
  >
    <VIcon name="search" />
  </VButton>
</template>
