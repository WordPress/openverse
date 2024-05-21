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
        @clear="handleClear($event)"
        @keydown.tab.native="hideRecentSearches"
      />
    </ClientOnly>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref } from "vue"

import { onClickOutside } from "@vueuse/core"

import { defineEvent } from "~/types/emits"

import { useRecentSearches } from "~/composables/use-recent-searches"

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
    const recentClasses = computed(() => {
      // Calculated by adding 8px to all heights defined in `VInputField.vue`.
      const FIELD_OFFSETS = {
        medium: "top-14",
      } as const
      return FIELD_OFFSETS[props.size]
    })
    const focusInput = () => {
      inputFieldRef.value?.focusInput()
    }

    /**
     * Hide recent searches on blur and click outside.
     */
    const handleSearchBlur = () => {
      if (!recent.entries.value.length) {
        recent.hide()
      }
    }

    const { handleKeydown, handleSelect, handleClear, recent } =
      useRecentSearches({
        handleSearch,
        focusInput,
        term: modelMedium,
        isMobile: false,
      })
    onClickOutside(searchBarEl, recent.hide)

    return {
      searchBarEl,
      inputFieldRef,

      handleSearch,
      modelMedium,

      showRecentSearches: recent.show,
      hideRecentSearches: recent.hide,
      handleSearchBlur,

      recentClasses,
      isRecentVisible: recent.isVisible,
      selectedIdx: recent.selectedIdx,
      entries: recent.entries,

      handleKeydown,
      handleSelect,
      handleClear,
    }
  },
})
</script>
