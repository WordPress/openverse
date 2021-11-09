<template>
  <div class="p-4">
    <div class="filterlist-header mt-4 mb-8">
      <h4 class="filter-heading">
        {{ $t('filter-list.filter-by') }}
      </h4>

      <button
        id="hide-filters-button"
        type="button"
        @click="onToggleSearchGridFilter()"
        @keyup.enter="onToggleSearchGridFilter()"
      >
        <span class="text-trans-blue hidden lg:block text-sm lowercase">{{
          $t('filter-list.hide')
        }}</span>
        <span class="me-4 text-lg lg:hidden">
          <i class="icon cross" />
        </span>
      </button>
    </div>
    <form class="filters-form" role="list">
      <FilterChecklist
        v-for="filterType in filterTypes"
        :key="filterType"
        role="listitem"
        :options="filters[filterType]"
        :title="filterTypeTitle(filterType)"
        :filter-type="filterType"
        @filterChanged="onUpdateFilter"
      />
    </form>
    <footer v-if="isAnyFilterApplied" class="flex justify-between">
      <button
        id="clear-filter-button"
        class="text-sm py-4 px-6 lowercase rounded"
        @click="onClearFilters"
      >
        {{ $t('filter-list.clear') }}
      </button>
      <button
        class="text-sm py-4 px-6 lowercase rounded bg-trans-blue text-white lg:hidden"
        @click="onToggleSearchGridFilter()"
      >
        {{ $t('filter-list.show') }}
      </button>
    </footer>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex'
import { kebabize } from '~/utils/format-strings'
import { AUDIO, IMAGE, VIDEO } from '~/constants/media'
import FilterChecklist from './FilterChecklist'
import { FILTER, SEARCH } from '~/constants/store-modules'

export default {
  name: 'FiltersList',
  components: {
    FilterChecklist,
  },
  computed: {
    ...mapState(SEARCH, ['searchType']),
    ...mapGetters(FILTER, [
      'audioFiltersForDisplay',
      'imageFiltersForDisplay',
      'videoFiltersForDisplay',
      'allFiltersForDisplay',
      'isAnyFilterApplied',
    ]),
    filters() {
      switch (this.searchType) {
        case AUDIO:
          return this.audioFiltersForDisplay
        case IMAGE:
          return this.imageFiltersForDisplay
        case VIDEO:
          return this.videoFiltersForDisplay
        default:
          return this.allFiltersForDisplay
      }
    },
    filterTypes() {
      return Object.keys(this.filters)
    },
  },
  methods: {
    filterTypeTitle(filterType) {
      if (filterType === 'searchBy') {
        return ''
      }
      return this.$t(`filters.${kebabize(filterType)}.title`)
    },
    onUpdateFilter({ code, filterType }) {
      this.$emit('onUpdateFilter', { code, filterType })
    },
    onToggleSearchGridFilter() {
      this.$emit('onToggleSearchGridFilter')
    },
    onClearFilters() {
      this.$emit('onClearFilters')
    },
  },
}
</script>

<style lang="scss" scoped>
.filterlist-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter-heading {
  font-size: 1rem;
}

#hide-filters-button {
  font-size: 0.813rem;
  font-weight: 500;
  margin-top: auto;
  margin-bottom: auto;
}

#clear-filter-button {
  color: #23282d;
  border: solid #23282d33 1px;
}
#clear-filter-button:hover {
  color: white;
  // @todo: Remove hardcoded colors
  background-color: #919496;
  border-color: #919496;
}
</style>
