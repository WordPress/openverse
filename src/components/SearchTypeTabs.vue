<template>
  <div>
    <section class="tabs">
      <ul role="tablist">
        <li
          v-for="type in contentTypes"
          :key="type"
          :aria-selected="activeTab == type"
          role="tab"
          :class="tabClass(type, 'tab')"
        >
          <nuxt-link
            aria-live="polite"
            class="is-size-5"
            :to="{ path: `/search/${type}`, query: $route.query }"
          >
            {{ capitalize(type) }}
          </nuxt-link>
        </li>
      </ul>
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
        'is-active': tabSlug === this.activeTab,
      }
    },
  },
}
</script>

<style scoped>
.tabs ul {
  padding-left: 24px;
}
</style>
