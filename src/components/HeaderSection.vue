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
import { mapState } from 'vuex'

export default {
  name: 'HeaderSection',
  props: {
    showNavSearch: { type: Boolean, default: false },
  },
  computed: mapState(['showNotification', 'isEmbedded']),
}
</script>
