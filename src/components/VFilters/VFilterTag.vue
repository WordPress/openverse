<template>
  <button
    class="button tiny tag"
    :aria-label="$t('filters.aria.remove-filter', { label: filterLabel })"
    @click="onClick"
  >
    <span>{{ filterLabel }}</span>
    <span class="close ms-2 p-2"><i class="icon cross" /></span>
  </button>
</template>
<script>
export default {
  name: 'VFilterTag',
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
