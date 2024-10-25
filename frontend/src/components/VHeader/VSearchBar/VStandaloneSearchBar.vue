<script setup lang="ts">
/**
 * Displays a search input for a search query and is attached to an action button
 * that fires a search request. Can contain other elements like the search type
 * popover. Is uncontrolled: Vue code does not try to set a default value when
 * hydrating the server-rendered code, so the value entered before full hydration
 * is not removed.
 */
import { ref } from "vue"

import VSearchButton from "~/components/VHeader/VSearchBar/VSearchButton.vue"

withDefaults(
  defineProps<{
    route?: "home" | "404"
    /**
     * Search bar should not have a focus box when a popover is open.
     */
    hasPopover?: boolean
  }>(),
  {
    route: "home",
    hasPopover: false,
  }
)

const emit = defineEmits<{
  submit: [string]
}>()

const inputRef = ref<HTMLInputElement | null>(null)

// Only emit `submit` if the input value is not blank
const handleSearch = () => {
  const searchTerm = inputRef.value?.value.trim()
  if (searchTerm) {
    emit("submit", searchTerm)
  }
}

const focusInput = () => {
  inputRef.value?.focus()
}

defineExpose({ focusInput })
</script>

<template>
  <!-- Form action is a fallback for when JavaScript is disabled. -->
  <form
    id="search-form"
    action="/search"
    role="search"
    class="group flex h-14 flex-row items-center rounded-sm border-tx bg-default sm:h-16 dark:bg-overlay"
    @submit.prevent="handleSearch"
  >
    <div
      class="input-field search-field group flex h-full flex-grow items-center overflow-hidden rounded-sm rounded-e-none border-1.5 border-e-0 pe-2"
      :class="[
        route === 'home' ? 'border-tx' : 'border-black dark:border-tx',
        { 'has-popover': hasPopover, black: route !== 'home' },
      ]"
    >
      <input
        id="search-bar"
        ref="inputRef"
        type="search"
        name="q"
        :placeholder="$t('hero.search.placeholder')"
        class="paragraph-large md:label-regular focus-visible:outline-style-none ms-4 h-full w-full appearance-none rounded-none bg-tx leading-none text-default placeholder-default"
        :aria-label="
          $t('search.searchBarLabel', {
            openverse: 'Openverse',
          })
        "
      />
      <!-- @slot Extra information goes here -->
      <slot />
    </div>
    <VSearchButton :route="route" />
  </form>
</template>

<style scoped>
.input-field:has(#search-bar:focus-visible) {
  @apply border-focus;
}

.input-field.has-popover:has(#search-bar:focus-visible) {
  @apply border-tx;
}
#search-form:has(button[type="submit"]:focus) .input-field.black {
  @apply border-tx;
}
</style>
