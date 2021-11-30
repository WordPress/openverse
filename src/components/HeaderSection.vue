<template>
  <header class="embedded">
    <NavSection :key="$route.path" :show-nav-search="showNavSearch" />
    <NotificationBanner v-if="showNotification" />
  </header>
</template>

<script>
export default {
  name: 'HeaderSection',
  props: {
    showNavSearch: { type: Boolean, default: false },
    showNotification: { type: Boolean, default: false },
  },
}
</script>
