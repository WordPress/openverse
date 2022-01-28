<template>
  <VIconButton
    v-bind="$attrs"
    :size="`search-${size}`"
    class="search-button hover:text-white group-hover:text-white hover:bg-pink group-hover:bg-pink p-0.5px ps-1.5px focus:p-0 border md:border border-dark-charcoal-20 hover:border-pink group-hover:border-pink rounded-e-sm active:shadow-ring"
    :icon-props="{ iconPath: searchIcon }"
    :aria-label="$t('search.search')"
    v-on="$listeners"
  />
</template>

<script>
import VIconButton from '~/components/VIconButton/VIconButton.vue'

import searchIcon from '~/assets/icons/search.svg'

export default {
  name: 'VSearchButton',
  components: { VIconButton },
  inheritAttrs: false,
  props: {
    size: {
      type: String,
      required: true,
      validator: (v) => ['small', 'medium', 'large', 'standalone'].includes(v),
    },
  },
  setup() {
    return { searchIcon }
  },
}
</script>

<style>
/* @todo: Find a better way to override the VIconButton border styles */
.search-button {
  /* Negative margin removes a tiny gap between the button and the input borders */
  margin-inline-start: -1px;
  border-inline-start-color: transparent;
  border-width: 1px;
}
.search-button.search-button:not(:hover):not(:focus):not(:focus-within) {
  border-inline-start-color: transparent;
  border-width: 1px;
}
.search-button.search-button:hover {
  border-inline-start-color: rgba(214, 212, 213, 1);
  border-width: 1px;
}
</style>
