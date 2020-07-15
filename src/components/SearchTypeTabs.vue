<template>
  <div>
    <section class="tabs">
      <ul>
        <li v-for="type in contentTypes" :key="type" :class="tabClass(type, 'tab')">
          <router-link
              class="is-size-5"
              :to="{ path: `/search/${type}`, query: $route.query }"
              :aria-selected="activeTab == type">
            {{ capitalize(type) }}
          </router-link>
        </li>
      </ul>
    </section>
  </div>
</template>

<script>
import { capitalize } from '@/utils/formatStrings';

export default {
  name: 'search-type-tabs',
  data() {
    return {
      contentTypes: ['image', 'audio', 'video'],
    };
  },
  computed: {
    activeTab() {
      return this.$route.path.split('search/')[1] || 'image';
    },
  },
  methods: {
    capitalize,
    tabClass(tabSlug, tabClass) {
      return {
        [tabClass]: true,
        'is-active': tabSlug === this.activeTab,
      };
    },
  },
};
</script>

<style>
</style>
