<template>
  <form
    class="search-bar group flex flex-row items-center rounded-sm border-tx bg-white"
    @submit.prevent="handleSearch"
  >
    <VInputFieldOld
      :placeholder="placeholder || $t('hero.search.placeholder')"
      v-bind="$attrs"
      class="search-field flex-grow border-dark-charcoal-20 focus:border-pink"
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
    </VInputFieldOld>
    <VSearchButtonOld type="submit" class="md:!h-12 md:!w-12" :size="size" />
  </form>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "@nuxtjs/composition-api"

import { defineEvent } from "~/types/emits"

import VInputFieldOld, {
  FIELD_SIZES,
} from "~/components/VInputFieldOld/VInputFieldOld.vue"
import VSearchButtonOld from "~/components/VHeaderOld/VSearchBar/VSearchButtonOld.vue"

/**
 * Displays a text field for a search query and is attached to an action button
 * that fires a search request. The loading state and number of hits are also
 * displayed in the bar itself.
 */
export default defineComponent({
  name: "VSearchBarOld",
  components: { VInputFieldOld, VSearchButtonOld },
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
    const searchText = computed(() => props.value)

    const updateSearchText = (val: string) => {
      emit("input", val)
    }

    const handleSearch = () => {
      emit("submit")
    }

    return {
      handleSearch,
      searchText,
      updateSearchText,
    }
  },
})
</script>
