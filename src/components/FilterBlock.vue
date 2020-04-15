<template>
    <span class="button tag" v-if="filterType === 'searchByCreator'">
      <span>Creator</span>
      <span @click="onClickCreator">&times;</span>
    </span>
    <span class="button tag" v-else>
      <span>{{ filter.name }}</span>
      <span @click="onClick">&times;</span>
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
