<template>
  <button
    class="filter-block button tiny tag mx-1"
    :aria-label="$t('filters.filter-tag-aria', { filterLabel: filterLabel })"
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
  name: 'FilterTag',
  props: {
    code: String,
    filterType: String,
    label: String,
  },
  computed: {
    needsTranslation() {
      return !['audioProviders', 'imageProviders'].includes(
        this.$props.filterType
      )
    },
    filterLabel() {
      return this.needsTranslation
        ? this.$t(this.$props.label)
        : this.$props.label
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
