<template>
  <div>
    <div class="filterlist-header">
      <h4>
        {{ $t('filter-list.filter-by') }}
      </h4>

      <button
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
      <button class="button tiny" @click="onClearFilters">
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
import { mapGetters } from 'vuex'
import { kebabize } from '~/utils/format-strings'
import { AUDIO, IMAGE, VIDEO } from '~/constants/media'
import FilterChecklist from './FilterChecklist'

export default {
  name: 'FiltersList',
  components: {
    FilterChecklist,
  },
  computed: {
    ...mapGetters([
      'audioFiltersForDisplay',
      'imageFiltersForDisplay',
      'videoFiltersForDisplay',
      'allFiltersForDisplay',
      'isAnyFilterApplied',
    ]),
    filters() {
      switch (this.$store.state.searchType) {
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
.filterlist-header h4 {
  display: inline-block;
  padding: 1.5rem 1rem 0 1.5rem;
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
</style>
