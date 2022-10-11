<template>
  <div ref="searchBarEl" class="relative">
    <form
      class="search-bar group flex flex-row items-center rounded-sm border-tx bg-white"
      :class="{ 'h-[57px] md:h-[69px]': size === 'standalone' }"
      @submit.prevent="handleSearch"
    >
      <VInputField
        v-bind="$attrs"
        v-model="modelMedium"
        :placeholder="placeholder || $t('hero.search.placeholder')"
        class="search-field flex-grow focus:border-pink"
        :class="[
          route === 'home'
            ? 'border-tx'
            : 'border-tx bg-dark-charcoal-10 text-dark-charcoal-70 focus-within:bg-white group-hover:bg-dark-charcoal-10 group-hover:text-dark-charcoal group-hover:focus-within:bg-white',
        ]"
        :label-text="
          $t('search.search-bar-label', { openverse: 'Openverse' }).toString()
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
        @focus="handleFocus"
        @keydown="handleKeydown"
      >
        <!-- @slot Extra information such as loading message or result count goes here. -->
        <slot />
      </VInputField>
      <VSearchButton type="submit" :size="size" :route="route" />
    </form>
    <ClientOnly>
      <VRecentSearches
        v-show="isNewHeaderEnabled && isRecentVisible"
        :selected-idx="selectedIdx"
        :entries="entries"
        class="absolute inset-x-0 lg:flex"
        :class="recentClasses"
        @select="handleSelect"
        @clear="handleClear"
      />
    </ClientOnly>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
} from '@nuxtjs/composition-api'

import { onClickOutside } from '@vueuse/core'

import { useMatchHomeRoute } from '~/composables/use-match-routes'
import { defineEvent } from '~/types/emits'

import { useSearchStore } from '~/stores/search'
import { useFeatureFlagStore } from '~/stores/feature-flag'

import { keycodes } from '~/constants/key-codes'

import { cyclicShift } from '~/utils/math'

import VInputField, {
  FIELD_SIZES,
} from '~/components/VInputField/VInputField.vue'
import VSearchButton from '~/components/VHeader/VSearchBar/VSearchButton.vue'
import VRecentSearches from '~/components/VRecentSearches/VRecentSearches.vue'

/**
 * Displays a text field for a search query and is attached to an action button
 * that fires a search request. The loading state and number of hits are also
 * displayed in the bar itself.
 */
export default defineComponent({
  name: 'VSearchBar',
  components: { VRecentSearches, VInputField, VSearchButton },
  inheritAttrs: false,
  props: {
    /**
     * the search query given as input to the field
     */
    value: {
      type: String,
      default: '',
    },
    size: {
      type: String as PropType<keyof typeof FIELD_SIZES>,
      required: true,
    },
    placeholder: {
      type: String,
      required: false,
    },
    is404: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    input: defineEvent<[string]>(),
    submit: defineEvent(),
  },
  setup(props, { emit }) {
    const searchBarEl = ref<HTMLElement | null>(null)

    const { matches: isHomeRoute } = useMatchHomeRoute()

    const route = computed(() => {
      return isHomeRoute?.value ? 'home' : props.is404 ? '404' : undefined
    })

    const modelMedium = computed<string>({
      get: () => props.value ?? '',
      set: (value: string) => {
        emit('input', value)
      },
    })

    const handleSearch = () => {
      emit('submit')
    }

    /* Focus */
    const handleFocus = () => {
      isRecentVisible.value = true
    }
    const handleBlur = () => {
      isRecentVisible.value = false
    }
    onClickOutside(searchBarEl, handleBlur)

    /* Recent searches */
    const featureFlagStore = useFeatureFlagStore()
    const isNewHeaderEnabled = featureFlagStore.isOn('new_header')

    const searchStore = useSearchStore()

    const isRecentVisible = ref(false)
    const recentClasses = computed(() => {
      // Calculated by adding 8px to all heights defined in `VInputField.vue`.
      const FIELD_OFFSETS = {
        small: 'top-12',
        medium: 'top-14',
        large: 'top-16',
        standalone: 'top-[65px] md:top-[77px]',
      } as const
      return FIELD_OFFSETS[props.size]
    })
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

      // Show the recent searches.
      isRecentVisible.value = true
      if (altKey) return

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

      if (key === keycodes.Enter && selectedIdx.value)
        // If a recent search is selected, populate its value into the input.
        modelMedium.value = entries.value[selectedIdx.value]

      if (([keycodes.Escape, keycodes.Enter] as string[]).includes(key))
        // Hide the recent searches.
        isRecentVisible.value = false

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

      isRecentVisible.value = false
      selectedIdx.value = undefined // Lose visual focus from entries.
      handleSearch() // Immediately execute the search manually.
    }
    /* Clear all recent searches from the store. */
    const handleClear = () => {
      searchStore.clearRecentSearches()
    }

    return {
      searchBarEl,

      handleSearch,
      route,
      modelMedium,

      handleFocus,
      handleBlur,

      isNewHeaderEnabled,
      isRecentVisible,
      recentClasses,
      selectedIdx,
      entries,

      handleKeydown,
      handleSelect,
      handleClear,
    }
  },
})
</script>

<style>
/* Removes the cross icon to clear the field */
.search-field input[type='search']::-webkit-search-decoration,
.search-field input[type='search']::-webkit-search-cancel-button,
.search-field input[type='search']::-webkit-search-results-button,
.search-field input[type='search']::-webkit-search-results-decoration {
  -webkit-appearance: none;
}
</style>
