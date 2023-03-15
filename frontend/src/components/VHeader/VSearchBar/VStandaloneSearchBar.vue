<template>
  <!-- Form action is a fallback for when JavaScript is disabled. -->
  <form
    action="/search"
    class="search-bar group flex h-14 flex-row items-center rounded-sm border-tx bg-white sm:h-16"
    @submit.prevent="handleSearch"
  >
    <div
      class="input-field search-field group flex h-full flex-grow items-center overflow-hidden rounded-sm border p-0.5px pe-2 rounded-e-none border-e-0 focus-within:border-1.5 focus-within:p-0 focus-within:pe-2 focus-within:border-e-0"
      :class="[
        isHomeRoute ? 'border-tx' : 'border-black',
        hasPopover ? 'focus-within:border-tx' : 'focus-within:border-pink',
      ]"
    >
      <input
        id="search-bar"
        ref="inputRef"
        type="search"
        name="q"
        :placeholder="$t('hero.search.placeholder').toString()"
        class="paragraph-large md:label-regular h-full w-full appearance-none rounded-none bg-tx leading-none text-dark-charcoal placeholder-dark-charcoal-70 ms-4 focus:outline-none"
        :aria-label="
          $t('search.search-bar-label', {
            openverse: 'Openverse',
          }).toString()
        "
      />
      <!-- @slot Extra information goes here -->
      <slot />
    </div>
    <VButton
      type="submit"
      :aria-label="$t('search.search')"
      size="disabled"
      :variant="isHomeRoute ? 'primary' : 'plain'"
      class="h-full w-14 flex-shrink-0 transition-none rounded-s-none sm:w-16"
      :class="{
        'search-button border-black p-0.5px ps-1.5px hover:bg-pink hover:text-white focus:border-tx focus-visible:bg-pink focus-visible:text-white group-focus-within:border-tx group-focus-within:bg-pink group-focus-within:text-white group-focus-within:hover:bg-dark-pink group-hover:border-tx group-hover:bg-pink group-hover:text-white group-focus:border-tx':
          !isHomeRoute,
      }"
    >
      <VIcon :icon-path="searchIcon" />
    </VButton>
  </form>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref } from "vue"

import { defineEvent } from "~/types/emits"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

import searchIcon from "~/assets/icons/search.svg"

/**
 * Displays a search input for a search query and is attached to an action button
 * that fires a search request. Can contain other elements like the search type
 * popover. Is uncontrolled: Vue code does not try to set a default value when
 * hydrating the server-rendered code, so the value entered before full hydration
 * is not removed.
 */
export default defineComponent({
  name: "VStandaloneSearchBar",
  components: { VButton, VIcon },
  props: {
    route: {
      type: String as PropType<"home" | "404">,
      default: "home",
    },
    /**
     * Search bar should not have a focus box when a popover is open.
     */
    hasPopover: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    submit: defineEvent<[string]>(),
  },
  setup(props, { emit }) {
    const inputRef = ref<HTMLInputElement | null>(null)

    // Only emit `submit` if the input value is not blank
    const handleSearch = () => {
      const searchTerm = inputRef.value?.value.trim()
      if (searchTerm) {
        emit("submit", searchTerm)
      }
    }

    const isHomeRoute = computed(() => props.route === "home")

    return {
      inputRef,
      handleSearch,
      isHomeRoute,

      searchIcon,
    }
  },
})
</script>
<style scoped>
.input-field {
  border-inline-end-width: 0;
}

.search-button {
  border-inline-start-width: 0;
}
</style>
