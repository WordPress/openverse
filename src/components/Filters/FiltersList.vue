<template>
  <div>
    <div class="filterlist-header">
      <h4 class="pt-6 pl-6 pr-4 inline-block">
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
      <FilterCheckList
        v-for="filterType in filterTypes"
        :key="filterType"
        role="listitem"
        :options="filters[filterType]"
        :disabled="licenseTypesDisabled"
        :title="filterTypeTitle(filterType)"
        :filter-type="filterType"
        @filterChanged="onUpdateFilter"
      />
    </form>
    <div v-if="isFilterApplied" class="clear-filters filter-buttons">
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
import FilterCheckList from './FilterChecklist'

export default {
  name: 'FiltersList',
  components: {
    FilterCheckList,
  },
  props: ['isFilterApplied', 'licenseTypesDisabled', 'licensesDisabled'],
  computed: {
    filters() {
      return this.$store.getters.getAllImageFilters
    },
    filterTypes() {
      return Object.keys(this.filters)
    },
    activeTab() {
      return this.$route.path.split('search/')[1] || 'image'
    },
  },
  methods: {
    filterTypeTitle(filterType) {
      const kebabize = (str) => {
        return str
          .split('')
          .map((letter, idx) => {
            return letter.toUpperCase() === letter
              ? `${idx !== 0 ? '-' : ''}${letter.toLowerCase()}`
              : letter
          })
          .join('')
      }
      if (filterType == 'searchBy') {
        return ''
      }
      return this.$t(`filters.${kebabize(filterType)}.title`)
    },
    onUpdateFilter({ code, filterType }) {
      this.$emit('onUpdateFilter', { code, filterType })
    },
    onUpdateSearchByCreator() {
      this.$emit('onUpdateSearchByCreator')
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
.scroll-y {
  overflow-y: scroll;
  height: calc(100vh - 84px);
}
.filter-buttons {
  padding: 1.5rem;
  text-align: center;
  @include desktop {
    padding: 0;
    padding-bottom: 1rem;
    margin: 1.5rem;
  }
}
.filter-buttons .button:first-child {
  margin-right: 1rem;
}
</style>
