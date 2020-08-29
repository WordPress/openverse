<template>
  <header>
    <NavSection :show-nav-search="showNavSearch" />
    <slot />
  </header>
</template>

<script>
export default {
  name: 'HeaderSection',
  props: { showNavSearch: { type: Boolean, default: false } },
}
</script>
