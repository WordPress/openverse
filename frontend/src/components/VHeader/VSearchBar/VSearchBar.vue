<script setup lang="ts">
/**
 * The search bar displayed on the search page.
 *
 * Displays a text field for a search query and is attached to an action button
 * that fires a search request. The loading state and number of hits are also
 * displayed in the bar itself.
 */
import { computed, ref, useAttrs, watch } from "vue"

import { onClickOutside } from "@vueuse/core"

import { useRecentSearches } from "~/composables/use-recent-searches"

import VInputField from "~/components/VInputField/VInputField.vue"
import VSearchButton from "~/components/VHeader/VSearchBar/VSearchButton.vue"
import VRecentSearches from "~/components/VRecentSearches/VRecentSearches.vue"

defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    /**
     * the search query given as input to the field
     */
    modelValue?: string
    placeholder?: string
  }>(),
  {
    modelValue: "",
  }
)

const emit = defineEmits<{
  "update:modelValue": [string]
  submit: []
  "recent-hidden": []
}>()
const attrs = useAttrs()
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
  // Calculated by adding 8px to the height of `VInputField.vue`.
  return "top-14"
})
const focusInput = () => {
  inputFieldRef.value?.focusInput()
}

/**
 * Hide recent searches on blur and click outside.
 */
const handleSearchBlur = () => {
  if (!entries.value.length) {
    hideRecentSearches()
  }
}

const {
  handleKeydown,
  handleSelect,
  handleClear,
  recent: {
    show: showRecentSearches,
    hide: hideRecentSearches,
    isVisible: isRecentVisible,
    selectedIdx,
    entries,
  },
} = useRecentSearches({
  focusInput,
  term: modelMedium,
  isMobile: false,
})
onClickOutside(searchBarEl, hideRecentSearches)

watch(isRecentVisible, (isVisible) => {
  if (!isVisible) {
    emit("recent-hidden")
  }
})

const nonClassAttrs = computed(() => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { class: _, ...rest } = attrs
  return rest
})
</script>

<template>
  <div ref="searchBarEl" class="relative" :class="$attrs.class">
    <!-- Form action is a fallback for when JavaScript is disabled. -->
    <form
      action="/search"
      role="search"
      class="search-bar group flex h-12 flex-row items-center rounded-sm border-tx bg-default"
      @submit.prevent="handleSearch"
    >
      <VInputField
        ref="inputFieldRef"
        v-bind="nonClassAttrs"
        v-model="modelMedium"
        :placeholder="placeholder || $t('hero.search.placeholder')"
        class="search-field flex-grow border-tx bg-secondary text-secondary focus-within:bg-default focus:border-focus group-hover:bg-secondary group-hover:text-default group-hover:focus-within:bg-default"
        :label-text="$t('search.searchBarLabel', { openverse: 'Openverse' })"
        :connection-sides="['end']"
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
