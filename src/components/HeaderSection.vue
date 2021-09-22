<template>
  <header :class="isEmbedded ? 'embedded' : ''">
    <EmbeddedNavSection
      v-if="isEmbedded"
      :key="$route.path"
      :show-nav-search="showNavSearch"
    />
    <NavSection v-else :key="$route.path" :show-nav-search="showNavSearch" />
    <NotificationBanner v-if="showNotification" />
  </header>
</template>

<script>
export default {
  name: 'HeaderSection',
  props: {
    isEmbedded: { type: Boolean, default: true },
    showNavSearch: { type: Boolean, default: false },
    showNotification: { type: Boolean, default: false },
  },
}
</script>
