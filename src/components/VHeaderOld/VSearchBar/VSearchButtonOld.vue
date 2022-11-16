<template>
  <VButton
    v-bind="$attrs"
    :aria-label="$t('search.search')"
    size="disabled"
    variant="plain"
    class="heading-6 search-button flex-shrink-0 border-dark-charcoal-20 p-0.5px transition-none ps-1.5px rounded-s-none hover:bg-pink hover:text-white focus-visible:bg-pink focus-visible:text-white group-focus-within:border-pink group-focus-within:bg-pink group-focus-within:text-white group-focus-within:hover:bg-dark-pink group-hover:border-pink group-hover:bg-pink group-hover:text-white"
    :class="sizeClasses"
    v-on="$listeners"
  >
    <VIcon :icon-path="searchIcon" />
  </VButton>
</template>

<script lang="ts">
import { defineComponent, computed, PropType } from '@nuxtjs/composition-api'

import VIcon from '~/components/VIcon/VIcon.vue'
import VButton from '~/components/VButton.vue'
import type { FieldSize } from '~/components/VInputFieldOld/VInputFieldOld.vue'

import searchIcon from '~/assets/icons/search.svg'

/**
 * The search button used in the search bar on the search page with the `old_header`.
 */
export default defineComponent({
  name: 'VSearchButtonOld',
  components: { VIcon, VButton },
  inheritAttrs: false,
  props: {
    size: {
      type: String as PropType<FieldSize>,
      required: true,
    },
  },
  setup(props) {
    const sizeClasses = computed(() => {
      return {
        small: 'w-10 md:w-12 h-10 md:h-12',
        medium: 'w-12 h-12',
        large: 'w-14 h-14',
      }[props.size]
    })

    return { searchIcon, sizeClasses }
  },
})
</script>

<style scoped>
.search-button {
  /* Removes a tiny gap between the button and the input borders */
  border-inline-start: 0;
}
</style>
