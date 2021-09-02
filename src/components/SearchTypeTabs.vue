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
        {{ tabTitle(type) }}
      </NuxtLink>
    </div>
  </section>
</template>

<script>
import { capitalize } from '~/utils/format-strings'
import { ALL_MEDIA, AUDIO, IMAGE, VIDEO } from '~/constants/media'
import { queryStringToSearchType } from '~/utils/search-query-transform'

export default {
  name: 'SearchTypeTabs',
  data() {
    return {
      contentTypes: [ALL_MEDIA, IMAGE, AUDIO, VIDEO],
    }
  },
  computed: {
    activeTab() {
      return queryStringToSearchType(this.$route.path)
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
      const pathType = type === ALL_MEDIA ? '' : type
      return this.localePath({
        path: `/search/${pathType}`,
        query: this.$route.query,
      })
    },
    tabTitle(type) {
      return this.capitalize(this.$t(`search-tab.${type}`))
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
