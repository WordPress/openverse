<template>
  <header>
    <NavSection
      :show-nav-search="showNavSearch"
      :nav-search-placeholder="navSearchPlaceholder"
    />
    <slot />
  </header>
</template>

<script>
export default {
  name: 'HeaderSection',
  props: ['showNavSearch', 'navSearchPlaceholder'],
}
</script>
