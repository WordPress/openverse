<template>
  <div>
    <section class="tabs">
      <ul>
        <li v-for="type in contentTypes" :key="type" :class="tabClass(type, 'tab')">
          <router-link class="is-size-5"
              :to="{ path: `/search/${type}`, query: $route.query }"
              :aria-selected="activeTab == type"
              @click.prevent="setActiveTab(type)">
            {{ capitalize(type) }}
          </router-link>
        </li>
      </ul>
    </section>
    <router-view />
  </div>
</template>

<script>
import { capitalize } from '@/utils/formatStrings';

export default {
  name: 'search-type-tabs',
  data() {
    return {
      contentTypes: ['image', 'audio', 'video'],
      activeTab: 'image',
    };
  },
  methods: {
    capitalize,
    tabClass(tabSlug, tabClass) {
      return {
        [tabClass]: true,
        'is-active': tabSlug === this.activeTab,
      };
    },
    setActiveTab(tabSlug) {
      this.activeTab = tabSlug;
      this.$router.push(`search/${tabSlug}`);
    },
  },
};
</script>

<style>
</style>
