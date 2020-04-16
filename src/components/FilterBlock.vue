<template>
    <span class="filter-block button tag margin-horizontal-smaller"
          v-if="filterType === 'searchByCreator'"
          aria-label="creator"
          role="filter">
      <span>Creator</span>
      <span class="close"
            tabindex="0"
            @click="onClickCreator">&#x2715;</span>
    </span>
    <span class="filter-block button tag margin-horizontal-smaller"
          role="filter"
          :aria-label="filter.name"
          v-else>
      <span>{{ filter.name }}</span>
      <span class="close"
            tabindex="0"
            @click="onClick">&#x2715;</span>
    </span>
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
<style lang="scss" scoped>
  .close {
    margin-left: 8px;
    margin-right: -6px;
  }
</style>
