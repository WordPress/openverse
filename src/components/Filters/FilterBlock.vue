<template>
  <button
    v-if="filterType === 'searchBy'"
    class="filter-block button tiny tag"
    :aria-label="label + 'filter'"
  >
    <span>{{ $props.label }}</span>
    <span
      :aria-label="$t('browse-page.aria.remove-filter')"
      class="close ml-2"
      tabindex="0"
      @click="onClickIsolatedFilter"
      @keyup.enter="onClickIsolatedFilter"
      ><i class="icon cross"
    /></span>
  </button>
  <button
    v-else
    class="filter-block button tiny tag mx-1"
    :aria-label="label + 'filter'"
  >
    <span>{{ $t($props.label) }}</span>
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
  methods: {
    onClick() {
      this.$emit('filterChanged', {
        code: this.$props.code,
        filterType: this.$props.filterType,
      })
    },
    onClickIsolatedFilter() {
      this.$emit('filterChanged', { filterType: this.$props.filterType })
    },
  },
}
</script>
<style lang="scss" scoped>
.filter-block {
  margin-left: 0.5rem;
}
</style>
