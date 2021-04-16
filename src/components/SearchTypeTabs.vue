<template>
  <div>
    <section class="search-tabs">
      <div role="tablist">
        <NuxtLink
          v-for="type in contentTypes"
          :id="type"
          :key="type"
          aria-live="polite"
          :to="localePath({ path: `/search/${type}`, query: $route.query })"
          :aria-selected="activeTab == type"
          :aria-controls="'tab-' + type"
          role="tab"
          :class="tabClass(type, 'tab')"
        >
          {{ capitalize(type) }}
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script>
import { capitalize } from '~/utils/formatStrings'

export default {
  name: 'SearchTypeTabs',
  data() {
    return {
      contentTypes: ['image', 'audio', 'video'],
    }
  },
  computed: {
    activeTab() {
      return this.$route.path.split('search/')[1] || 'image'
    },
  },
  methods: {
    capitalize,
    tabClass(tabSlug, tabClass) {
      return {
        [tabClass]: true,
        'is-size-5': true,
        'is-active': tabSlug === this.activeTab,
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '~/styles/bulma/utilities/_all';
@import '~/styles/vocabulary/typography';
@import '~/styles/tabs.scss';
.search-tabs {
  margin-left: 1rem;
}
</style>
