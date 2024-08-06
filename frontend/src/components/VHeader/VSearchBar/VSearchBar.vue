<template>
  <div ref="searchBarEl" class="relative" :class="$attrs.class">
    <!-- Form action is a fallback for when JavaScript is disabled. -->
    <form
      action="/search"
      role="search"
      class="search-bar bg-default group flex h-12 flex-row items-center rounded-sm border-tx"
      @submit.prevent="handleSearch"
    >
      <VInputField
        ref="inputFieldRef"
        v-bind="nonClassAttrs"
        v-model="modelMedium"
        :placeholder="placeholder || $t('hero.search.placeholder')"
        class="search-field focus-within:bg-default group-hover:text-default group-hover:focus-within:bg-default flex-grow border-tx bg-fill-secondary text-secondary focus:border-focus group-hover:bg-fill-secondary"
        :label-text="$t('search.searchBarLabel', { openverse: 'Openverse' })"
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
        @keydown.tab.exact="handleSearchBlur"
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
        @keydown.tab="hideRecentSearches"
      />
    </ClientOnly>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref, watch } from "vue"

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
    modelValue: {
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
    "update:modelValue": defineEvent<[string]>(),
    submit: defineEvent(),
    "recent-hidden": defineEvent(),
  },
  setup(props, { attrs, emit }) {
    const searchBarEl = ref<HTMLElement | null>(null)
    const inputFieldRef = ref<InstanceType<typeof VInputField> | null>(null)

    const modelMedium = computed<string>({
      get: () => props.modelValue ?? "",
      set: (value: string) => {
        emit("update:modelValue", value)
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
        focusInput,
        term: modelMedium,
        isMobile: false,
      })
    onClickOutside(searchBarEl, recent.hide)

    watch(recent.isVisible, (isVisible) => {
      if (!isVisible) {
        emit("recent-hidden")
      }
    })

    const nonClassAttrs = computed(() => {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { class: _, ...rest } = attrs
      return rest
    })

    return {
      searchBarEl,
      inputFieldRef,

      nonClassAttrs,

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
