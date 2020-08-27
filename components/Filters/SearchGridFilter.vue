<template>
  <div
    :class="{
      'search-filters': true,
      'search-filters__visible': isFilterVisible,
    }"
  >
    <filters-list
      :filters="filters"
      :isFilterApplied="isFilterApplied"
      :licenseTypesDisabled="licenseTypesDisabled"
      :licensesDisabled="licensesDisabled"
      @onUpdateFilter="onUpdateFilter"
      @onUpdateSearchByCreator="onUpdateSearchByCreator"
      @onToggleSearchGridFilter="onToggleSearchGridFilter"
      @onClearFilters="onClearFilters"
    />
  </div>
</template>

<script>
import { SET_FILTER_IS_VISIBLE, CLEAR_FILTERS } from '../store/mutation-types'
import { TOGGLE_FILTER } from '../store/action-types'
import { ExperimentData } from '@/abTests/experiments/filterExpansion'
import FiltersList from './FiltersList'

export default {
  name: 'search-grid-filter',
  props: ['provider'],
  components: {
    FiltersList,
  },
  computed: {
    isFilterApplied() {
      return this.$store.state.isFilterApplied
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible
    },
    filters() {
      return this.$store.state.filters
    },
    licensesDisabled() {
      return this.$store.state.filters.licenseTypes.some((li) => li.checked)
    },
    licenseTypesDisabled() {
      return this.$store.state.filters.licenses.some((li) => li.checked)
    },
    filtersExpandedByDefault() {
      const experiment = this.$store.state.experiments.find(
        (exp) => exp.name === ExperimentData.EXPERIMENT_NAME
      )
      return experiment
        ? experiment.case === ExperimentData.FILTERS_EXPANDED_CASE
        : false
    },
  },
  methods: {
    onUpdateFilter({ code, filterType }) {
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType,
        provider: this.$props.provider,
        shouldNavigate: true,
      })
    },
    onClearFilters() {
      this.$store.commit(CLEAR_FILTERS, {
        provider: this.$props.provider,
        shouldNavigate: true,
      })
    },
    onUpdateSearchByCreator() {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'searchBy',
        provider: this.$props.provider,
        shouldNavigate: true,
      })
    },
    onToggleSearchGridFilter() {
      this.$store.commit(SET_FILTER_IS_VISIBLE, {
        isFilterVisible: !this.isFilterVisible,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'bulma/sass/utilities/_all.sass';

.search-filters {
  display: none;
  height: auto;
  max-height: 100%;
  overflow-y: scroll;

  label {
    color: #333333;
  }

  @include touch {
    width: 21.875rem;
    max-height: 37rem;
    overflow-x: hidden;
  }

  &__visible {
    border-top: 1px solid #e8e8e8;
    display: block;
  }
}
</style>
