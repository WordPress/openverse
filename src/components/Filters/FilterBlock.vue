<template>
  <button
    v-if="filterType === 'searchBy'"
    class="filter-block button tiny tag margin-horizontal-smaller"
    :aria-label="label + 'filter'"
  >
    <span>{{ this.$props.label }}</span>
    <span
      :aria-label="$t('browse-page.aria.remove-filter')"
      class="close margin-left-small"
      tabindex="0"
      @click="onClickIsolatedFilter"
      @keyup.enter="onClickIsolatedFilter"
      ><i class="icon cross"
    /></span>
  </button>
  <button
    v-else
    class="filter-block button tiny tag margin-horizontal-smaller margin-bottom-smaller"
    :aria-label="label + 'filter'"
  >
    <span>{{ $t(this.$props.label) }}</span>
    <span
      class="close margin-left-small padding-small"
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
