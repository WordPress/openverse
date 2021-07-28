<template>
  <button
    class="filter-block button tiny tag mx-1"
    :aria-label="filterLabel + ' filter'"
  >
    <span>{{ filterLabel }}</span>
    <span
      class="close ml-2 p-2"
      tabindex="0"
      @click="onClick"
      @keyup.enter="onClick"
      ><i class="icon cross"
    /></span>
  </button>
</template>
<script>
export default {
  name: 'FilterBlock',
  props: ['code', 'filterType', 'label'],
  computed: {
    filterLabel() {
      return this.$props.filterType === 'providers'
        ? this.$props.label
        : this.$t(this.$props.label)
    },
  },
  methods: {
    onClick() {
      this.$emit('filterChanged', {
        code: this.$props.code,
        filterType: this.$props.filterType,
      })
    },
  },
}
</script>
<style lang="scss" scoped>
.filter-block {
  margin-left: 0.5rem;
}
</style>
