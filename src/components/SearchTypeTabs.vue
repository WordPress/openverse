<template>
  <section class="tabs">
    <div role="tablist">
      <NuxtLink
        v-for="type in contentTypes"
        :id="type"
        :key="type"
        aria-live="polite"
        :to="tabPath(type)"
        :aria-selected="activeTab == type"
        :aria-controls="'tab-' + type"
        role="tab"
        :class="tabClass(type, 'tab')"
      >
        {{ capitalize(type) }}
      </NuxtLink>
    </div>
  </section>
</template>

<script>
import { capitalize } from '~/utils/formatStrings'

export default {
  name: 'SearchTypeTabs',
  data() {
    return {
      contentTypes: ['all', 'image', 'audio', 'video'],
    }
  },
  computed: {
    activeTab() {
      return this.$route.path.split('search/')[1] || 'all'
    },
  },
  methods: {
    capitalize,
    tabClass(tabSlug, tabClass) {
      return {
        [tabClass]: true,
        'text-lg': true,
        'is-active': tabSlug === this.activeTab,
      }
    },
    tabPath(type) {
      const pathType = type === 'all' ? '' : type
      return this.localePath({
        path: `/search/${pathType}`,
        query: this.$route.query,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.tabs {
  background-color: white;
  padding-left: 1.5rem;
  border-bottom: 1px solid $color-transition-gray;
}

.tabs [role='tablist'] {
  border-bottom: none;
}

.tab:not(.is-active):not(:hover) {
  color: #929496;
}
</style>
