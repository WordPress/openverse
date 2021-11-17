<template>
  <button
    :type="type"
    class="search-button flex items-center justify-center h-12 w-12 hover:text-white group-hover:text-white hover:bg-pink group-hover:bg-pink p-0.5px ps-1.5px focus:p-0 border border-s-0 focus:border-1.5 border-dark-charcoal-20 hover:border-pink group-hover:border-pink focus:border-pink rounded-e-sm focus:outline-none"
    :aria-label="$t('search.search')"
    v-on="$listeners"
  >
    <svg
      class="h-6 w-6"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <use :href="`${searchIcon}#icon`" />
    </svg>
    <span class="sr-only">{{ $t('search.search') }}</span>
  </button>
</template>

<script>
import searchIcon from '~/assets/icons/search.svg'

export default {
  name: 'SearchButton',
  setup(props, { attrs }) {
    const type = attrs['type'] ?? 'button'

    return {
      searchIcon,

      type,
    }
  },
}
</script>

<style scoped>
.search-button:active {
  box-shadow: 0 0 0 1px inset white;
}
</style>
