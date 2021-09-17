<template>
  <div>
    <div class="filterlist-header">
      <h4 class="filter-heading">
        {{ $t('filter-list.filter-by') }}
      </h4>

      <button
        id="hide-filters-button"
        type="button"
        class="button is-text tiny p-0 mt-6 mr-2 report float-right"
        @click="onToggleSearchGridFilter()"
        @keyup.enter="onToggleSearchGridFilter()"
      >
        <span class="text-trans-blue hidden desk:block text-sm lowercase">{{
          $t('filter-list.hide')
        }}</span>
        <span class="mr-4 text-lg desk:hidden">
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
    <div v-if="isAnyFilterApplied" class="clear-filters filter-buttons">
      <button
        id="clear-filter-button"
        class="button tiny"
        @click="onClearFilters"
      >
        {{ $t('filter-list.clear') }}
      </button>
      <button
        class="button is-primary tiny is-hidden-desktop"
        @click="onToggleSearchGridFilter()"
      >
        {{ $t('filter-list.show') }}
      </button>
    </div>
  </div>
</template>

<script>
import { kebabize } from '~/utils/format-strings'
import { AUDIO, IMAGE, VIDEO } from '~/constants/media'
import FilterChecklist from './FilterChecklist'

export default {
  name: 'FiltersList',
  components: {
    FilterChecklist,
  },
  computed: {
    filters() {
      switch (this.$store.state.searchType) {
        case AUDIO:
          return this.$store.getters.audioFiltersForDisplay
        case IMAGE:
          return this.$store.getters.imageFiltersForDisplay
        case VIDEO:
          return this.$store.getters.videoFiltersForDisplay
        default:
          return this.$store.getters.allFiltersForDisplay
      }
    },
    filterTypes() {
      return Object.keys(this.filters)
    },
    isAnyFilterApplied() {
      return this.$store.getters.isAnyFilterApplied
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
  padding-left: 52px;
  padding-top: 31px;
  padding-bottom: 16px;
  margin: 0;
}
.filterlist-header h4 {
  display: inline-block;
}

.filter-heading {
  font-size: 1rem;
}

.filter-buttons {
  padding: 1.5rem;
  text-align: center;
  @include desktop {
    padding: 0 0 1rem;
    margin: 1.5rem;
  }
}
.filter-buttons .button:first-child {
  margin-right: 1rem;
}

#hide-filters-button {
  font-size: 13px;
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
  background-color: #919496;
  border: none;
}

.filter-buttons {
  display: flex;
  justify-content: space-between;
  margin: 0;
  padding-top: 1rem;
  padding-left: 52px;
}

.filter-buttons button {
  width: 118px;
  height: 48px;
  font-size: 13px;
  font-weight: 500;
}
</style>
