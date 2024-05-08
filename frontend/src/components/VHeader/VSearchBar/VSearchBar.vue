<template>
  <div ref="searchBarEl" class="relative">
    <!-- Form action is a fallback for when JavaScript is disabled. -->
    <form
      action="/search"
      role="search"
      class="search-bar group flex h-12 flex-row items-center rounded-sm border-tx bg-white"
      @submit.prevent="handleSearch"
    >
      <VInputField
        ref="inputFieldRef"
        v-bind="$attrs"
        v-model="modelMedium"
        :placeholder="placeholder || $t('hero.search.placeholder')"
        class="search-field flex-grow border-tx bg-dark-charcoal-10 text-dark-charcoal-70 focus-within:bg-white focus:border-pink group-hover:bg-dark-charcoal-10 group-hover:text-dark-charcoal group-hover:focus-within:bg-white"
        :label-text="
          $t('search.searchBarLabel', { openverse: 'Openverse' }).toString()
        "
        :connection-sides="['end']"
        :size="size"
        field-id="search-bar"
        type="search"
        autocomplete="off"
        name="q"
        role="combobox"
        aria-autocomplete="none"
        :aria-expanded="isRecentVisible"
        aria-controls="recent-searches-list"
        :aria-activedescendant="
          selectedIdx !== undefined ? `option-${selectedIdx}` : undefined
        "
        @focus="showRecentSearches"
        @keydown="handleKeydown"
      >
        <!-- @slot Extra information such as loading message or result count goes here. -->
        <slot />
      </VInputField>
      <VSearchButton
        type="submit"
        route="search"
        @keydown.tab="handleSearchBlur"
      />
    </form>
    <ClientOnly>
      <VRecentSearches
        v-show="isRecentVisible"
        :selected-idx="selectedIdx"
        :entries="entries"
        class="absolute inset-x-0 z-popover lg:flex"
        :class="recentClasses"
        @select="handleSelect"
        @clear="handleClear"
        @clear-single="handleClearSingle"
        @keydown.tab.native="hideRecentSearches"
      />
    </ClientOnly>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref } from "vue"

import { onClickOutside } from "@vueuse/core"

import { defineEvent } from "~/types/emits"

import { useSearchStore } from "~/stores/search"

import { keycodes } from "~/constants/key-codes"

import { cyclicShift } from "~/utils/math"

import VInputField, {
  FIELD_SIZES,
} from "~/components/VInputField/VInputField.vue"
import VSearchButton from "~/components/VHeader/VSearchBar/VSearchButton.vue"
import VRecentSearches from "~/components/VRecentSearches/VRecentSearches.vue"

/**
 * The search bar displayed on the search page.
 *
 * Displays a text field for a search query and is attached to an action button
 * that fires a search request. The loading state and number of hits are also
 * displayed in the bar itself.
 */
export default defineComponent({
  name: "VSearchBar",
  components: { VRecentSearches, VInputField, VSearchButton },
  inheritAttrs: false,
  props: {
    /**
     * the search query given as input to the field
     */
    value: {
      type: String,
      default: "",
    },
    size: {
      type: String as PropType<keyof typeof FIELD_SIZES>,
      default: "medium",
    },
    placeholder: {
      type: String,
      required: false,
    },
  },
  emits: {
    input: defineEvent<[string]>(),
    submit: defineEvent(),
  },
  setup(props, { emit }) {
    const searchBarEl = ref<HTMLElement | null>(null)
    const inputFieldRef = ref<InstanceType<typeof VInputField> | null>(null)

    const modelMedium = computed<string>({
      get: () => props.value ?? "",
      set: (value: string) => {
        emit("input", value)
      },
    })

    const handleSearch = () => {
      emit("submit")
    }

    /* Recent searches */
    const searchStore = useSearchStore()

    const isRecentVisible = ref(false)
    const recentClasses = computed(() => {
      // Calculated by adding 8px to all heights defined in `VInputField.vue`.
      const FIELD_OFFSETS = {
        medium: "top-14",
      } as const
      return FIELD_OFFSETS[props.size]
    })

    /**
     * Show and hide recent searches.
     */
    const showRecentSearches = () => {
      isRecentVisible.value = true
    }
    const hideRecentSearches = () => {
      isRecentVisible.value = false
    }
    /**
     * Hide recent searches on blur and click outside.
     */
    const handleSearchBlur = () => {
      if (!entries.value.length) {
        hideRecentSearches()
      }
    }
    onClickOutside(searchBarEl, hideRecentSearches)

    /**
     * Refers to the current suggestion that has visual focus (not DOM focus)
     * and is the active descendant. This should be set to `undefined` when the
     * visual focus is on the input field.
     */
    const selectedIdx = ref<number | undefined>(undefined)
    const entries = computed(() => searchStore.recentSearches)

    const handleVerticalArrows = (event: KeyboardEvent) => {
      event.preventDefault() // Prevent the cursor from moving horizontally.
      const { key, altKey } = event

      showRecentSearches()
      if (altKey) {
        return
      }

      // Shift selection (if Alt was not pressed with arrow keys)
      let defaultValue: number
      let offset: number
      if (key == keycodes.ArrowUp) {
        defaultValue = 0
        offset = -1
      } else {
        defaultValue = -1
        offset = 1
      }
      selectedIdx.value = cyclicShift(
        selectedIdx.value ?? defaultValue,
        offset,
        0,
        entries.value.length
      )
    }

    const handleOtherKeys = (event: KeyboardEvent) => {
      const { key } = event

      if (key === keycodes.Enter && selectedIdx.value) {
        // If a recent search is selected, populate its value into the input.
        modelMedium.value = entries.value[selectedIdx.value]
      }

      // Hide the recent searches popover when the user presses Enter, Escape or Shift+Tab on the input.
      if (
        (key === keycodes.Tab && event.shiftKey) ||
        ([keycodes.Escape, keycodes.Enter] as string[]).includes(key)
      ) {
        hideRecentSearches()
      }

      selectedIdx.value = undefined // Lose visual focus from entries.
    }
    const handleKeydown = (event: KeyboardEvent) => {
      const { key } = event

      return ([keycodes.ArrowUp, keycodes.ArrowDown] as string[]).includes(key)
        ? handleVerticalArrows(event)
        : handleOtherKeys(event)
    }

    /* Populate the input with the clicked entry and execute the search. */
    const handleSelect = (idx: number) => {
      modelMedium.value = entries.value[idx]

      hideRecentSearches()
      selectedIdx.value = undefined // Lose visual focus from entries.
      handleSearch() // Immediately execute the search manually.
    }
    /* Clear all recent searches from the store. */
    const handleClear = () => {
      inputFieldRef.value?.focusInput()
      searchStore.clearRecentSearches()
    }
    /* Clear a specific recent search from the store. */
    const handleClearSingle = (idx: number) => {
      inputFieldRef.value?.focusInput()
      searchStore.clearRecentSearch(idx)
    }

    return {
      searchBarEl,
      inputFieldRef,

      handleSearch,
      modelMedium,

      showRecentSearches,
      hideRecentSearches,
      handleSearchBlur,

      isRecentVisible,
      recentClasses,
      selectedIdx,
      entries,

      handleKeydown,
      handleSelect,
      handleClear,
      handleClearSingle,
    }
  },
})
</script>
