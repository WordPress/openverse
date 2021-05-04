<template>
  <header>
    <NavSection :key="$route.path" :show-nav-search="showNavSearch" />
    <NotificationBanner v-if="showNotification" />
  </header>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'HeaderSection',
  props: { showNavSearch: { type: Boolean, default: false } },
  computed: mapState(['showNotification']),
}
</script>
