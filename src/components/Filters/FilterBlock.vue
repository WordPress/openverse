<template>
    <button class="filter-block button tiny tag margin-horizontal-smaller"
            v-if="filterType === 'searchBy' || filterType === 'mature'"
            role="filter"
            :aria-label="label">
      <span>{{ this.$props.label }}</span>
      <span class="close margin-left-small"
            tabindex="0"
            @click="onClickIsolatedFilter"><i class="icon cross" /></span>
    </button>
    <button v-else
            class="filter-block button tiny tag margin-horizontal-smaller margin-bottom-smaller"
            role="filter"
            :aria-label="label">
      <span>{{ this.$props.label }}</span>
      <span class="close padding-left-normal"
            tabindex="0"
            @click="onClick"><i class="icon cross" /></span>
    </button>
</template>
<script>
export default {
  name: 'filter-block',
  props: ['code', 'filterType', 'label'],
  methods: {
    onClick() {
      this.$emit('filterChanged', { code: this.$props.code, filterType: this.$props.filterType });
    },
    onClickIsolatedFilter() {
      this.$emit('filterChanged', { filterType: this.$props.filterType });
    },
  },
};
</script>

