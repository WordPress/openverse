<template>
  <form
    class="search-bar group flex h-[57px] flex-row items-center rounded-sm border-tx bg-white md:h-[69px]"
    @submit.prevent="handleSearch"
  >
    <div
      class="input-field search-field group flex h-full flex-grow items-center overflow-hidden rounded-sm border p-0.5px pe-1.5px rounded-e-none border-e-0 focus-within:border-1.5 focus-within:border-pink focus-within:bg-dark-charcoal-06 focus-within:p-0 group-hover:bg-dark-charcoal-06"
      :class="[isHomeRoute ? 'border-tx' : 'border-dark-charcoal-20']"
    >
      <input
        id="search-bar"
        ref="inputRef"
        type="search"
        name="q"
        :placeholder="
          $t(
            isHomeRoute ? 'hero.search.placeholder' : '404.search-placeholder'
          ).toString()
        "
        class="h-full w-full appearance-none rounded-none bg-tx text-base leading-none text-dark-charcoal placeholder-dark-charcoal-70 ms-4 focus:outline-none md:text-2xl"
        :aria-label="
          isHomeRoute
            ? $t('search.search-bar-label', {
                openverse: 'Openverse',
              }).toString()
            : $t('404.search-placeholder').toString()
        "
      />
      <!-- @slot Extra information goes here -->
      <slot />
    </div>
    <VSearchButtonOld type="submit" size="standalone" :route="route" />
  </form>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
} from '@nuxtjs/composition-api'

import { defineEvent } from '~/types/emits'

import VSearchButtonOld from '~/components/VHeaderOld/VSearchBar/VSearchButtonOld.vue'

/**
 * Displays a search input for a search query and is attached to an action button
 * that fires a search request. Can contain other elements like the search type
 * popover. Is uncontrolled: Vue code does not try to set a default value when
 * hydrating the server-rendered code, so the value entered before full hydration
 * is not removed.
 */
export default defineComponent({
  name: 'VStandaloneSearchBarOld',
  components: { VSearchButtonOld },
  props: {
    route: {
      type: String as PropType<'home' | '404'>,
      default: 'home',
    },
  },
  emits: {
    submit: defineEvent(),
  },
  setup(props, { emit }) {
    const inputRef = ref<HTMLInputElement | null>(null)

    const handleSearch = () => {
      const searchTerm = inputRef.value?.value.trim()
      emit('submit', searchTerm)
    }

    const isHomeRoute = computed(() => props.route === 'home')

    return {
      inputRef,
      handleSearch,
      isHomeRoute,
    }
  },
})
</script>
