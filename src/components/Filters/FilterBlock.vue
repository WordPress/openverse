<template>
    <button class="filter-block button tiny tag margin-horizontal-smaller"
          v-if="filterType === 'searchByCreator'"
          aria-label="creator"
          role="filter">
      <span>Creator</span>
      <span class="close margin-left-small"
            tabindex="0"
            @click="onClickCreator"><i class="icon cross" /></span>
    </button>
    <button class="filter-block button tiny tag margin-horizontal-smaller"
          role="filter"
          :aria-label="filter.name"
          v-else>
      <span>{{ filter.name }}</span>
      <span class="close padding-left-normal"
            tabindex="0"
            @click="onClick"><i class="icon cross" /></span>
    </button>
</template>
<script>
export default {
  name: 'filter-block',
  props: ['filter', 'filterType'],
  methods: {
    onClick() {
      this.$emit('filterChanged', { code: this.filter.code, filterType: this.$props.filterType });
    },
    onClickCreator() {
      this.$emit('filterChanged', { code: this.filter.code });
    },
  },
};
</script>

