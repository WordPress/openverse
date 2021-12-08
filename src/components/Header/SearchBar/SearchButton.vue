<template>
  <VIconButton
    v-bind="$attrs"
    size="search"
    class="search-button hover:text-white group-hover:text-white hover:bg-pink group-hover:bg-pink p-0.5px ps-1.5px focus:p-0 border border-s-0 focus:border-1.5 border-dark-charcoal-20 hover:border-pink group-hover:border-pink rounded-e-sm active:shadow-ring"
    :icon-props="{ iconPath: searchIcon }"
    :aria-label="$t('search.search')"
    v-on="$listeners"
  />
</template>

<script>
import VIconButton from '~/components/VIconButton/VIconButton.vue'

import searchIcon from '~/assets/icons/search.svg'

export default {
  name: 'SearchButton',
  components: { VIconButton },
  inheritAttrs: false,
  setup() {
    return { searchIcon }
  },
}
</script>
