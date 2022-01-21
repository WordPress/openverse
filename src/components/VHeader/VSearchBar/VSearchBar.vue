<template>
  <form
    class="search-bar group flex flex-row items-center bg-white rounded-sm"
    @submit.prevent="handleSearch"
  >
    <VInputField
      v-bind="$attrs"
      class="flex-grow search-field"
      :label-text="$t('hero.aria.search')"
      :connection-sides="['end']"
      field-id="search-bar"
      type="search"
      name="q"
      :model-value="searchText"
      @update:modelValue="updateSearchText"
    >
      <!-- @slot Extra information such as loading message or result count goes here. -->
      <slot />
    </VInputField>
    <VSearchButton type="submit" />
  </form>
</template>

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'

import VInputField from '~/components/VInputField/VInputField.vue'
import VSearchButton from '~/components/VHeader/VSearchBar/VSearchButton.vue'

/**
 * Displays a text field for a search query and is attached to an action button
 * that fires a search request. The loading state and number of hits are also
 * displayed in the bar itself.
 */
const VSearchBar = defineComponent({
  name: 'VSearchBar',
  components: {
    VInputField,
    VSearchButton,
  },
  inheritAttrs: false,
  props: {
    /**
     * the search query given as input to the field
     */
    value: {
      type: String,
      default: '',
    },
  },
  emits: ['input', 'submit'],
  setup(props, { emit }) {
    const searchText = computed(() => props.value)
    const updateSearchText = (val) => {
      emit('input', val)
    }

    const handleSearch = () => {
      emit('submit')
    }

    return {
      handleSearch,
      searchText,
      updateSearchText,
    }
  },
})
export default VSearchBar
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
