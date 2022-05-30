<template>
  <form
    class="search-bar group flex flex-row items-center bg-white rounded-sm"
    @submit.prevent="handleSearch"
  >
    <VInputField
      :placeholder="placeholder || $t('hero.search.placeholder')"
      v-bind="$attrs"
      class="flex-grow search-field"
      :class="{ 'border-transparent': isHomeRoute }"
      :label-text="
        $t('search.search-bar-label', { openverse: 'Openverse' }).toString()
      "
      :connection-sides="['end']"
      :size="size"
      field-id="search-bar"
      type="search"
      name="q"
      :model-value="searchText"
      @update:modelValue="updateSearchText"
    >
      <!-- @slot Extra information such as loading message or result count goes here. -->
      <slot />
    </VInputField>
    <VSearchButton type="submit" :size="size" :is-home-route="isHomeRoute" />
  </form>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { useMatchHomeRoute } from '~/composables/use-match-routes'
import { defineEvent } from '~/types/emits'

import VInputField, {
  FIELD_SIZES,
} from '~/components/VInputField/VInputField.vue'
import VSearchButton from '~/components/VHeader/VSearchBar/VSearchButton.vue'

/**
 * Displays a text field for a search query and is attached to an action button
 * that fires a search request. The loading state and number of hits are also
 * displayed in the bar itself.
 */
export default defineComponent({
  name: 'VSearchBar',
  components: { VInputField, VSearchButton },
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
  },
  emits: {
    input: defineEvent<[string]>(),
    submit: defineEvent(),
  },
  setup(props, { emit }) {
    const { matches: isHomeRoute } = useMatchHomeRoute()

    const searchText = computed(() => props.value)

    const updateSearchText = (val: string) => {
      emit('input', val)
    }

    const handleSearch = () => {
      emit('submit')
    }

    return {
      handleSearch,
      isHomeRoute,
      searchText,
      updateSearchText,
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
