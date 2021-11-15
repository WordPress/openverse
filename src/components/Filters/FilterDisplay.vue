<template>
  <div class="flex flex-wrap items-center p-4" aria-live="polite">
    <span v-if="isAnyFilterApplied" class="me-2 font-semibold mb-2">
      {{ $t('filters.filter-by') }}
    </span>
    <FilterTag
      v-for="filter in appliedFilterTags"
      :key="filter.code"
      class="mx-1 mb-2 ms-2"
      :code="filter.code"
      :label="filter.name"
      :filter-type="filter.filterType"
      @filterChanged="onUpdateFilter"
    />
  </div>
</template>

<script>
import { TOGGLE_FILTER } from '~/constants/action-types'
import FilterTag from '~/components/Filters/FilterTag'
import { mapGetters } from 'vuex'
import { SEARCH } from '~/constants/store-modules'

export default {
  name: 'FilterDisplay',
  components: { FilterTag },
  computed: {
    ...mapGetters(SEARCH, ['appliedFilterTags', 'isAnyFilterApplied']),
  },
  methods: {
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(`${SEARCH}/${TOGGLE_FILTER}`, { code, filterType })
    },
  },
}
</script>
