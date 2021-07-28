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
    <form :class="{ 'filters-form': true }" role="list">
      <FilterCheckList
        role="listitem"
        :options="filters.licenseTypes"
        :disabled="licenseTypesDisabled"
        :title="$t('filters.license-types.title')"
        filter-type="licenseTypes"
        @filterChanged="onUpdateFilter"
      />
      <FilterCheckList
        v-if="activeTab == 'image'"
        role="listitem"
        :options="filters.licenses"
        :disabled="licensesDisabled"
        :title="$t('filters.licenses.title')"
        filter-type="licenses"
        @filterChanged="onUpdateFilter"
      />
      <FilterCheckList
        v-if="activeTab == 'image'"
        role="listitem"
        :options="filters.providers"
        :title="$t('filters.providers.title')"
        filter-type="providers"
        @filterChanged="onUpdateFilter"
      />
      <FilterCheckList
        v-if="activeTab == 'image'"
        role="listitem"
        :options="filters.categories"
        :title="$t('filters.categories.title')"
        filter-type="categories"
        @filterChanged="onUpdateFilter"
      />
      <FilterCheckList
        v-if="activeTab == 'image'"
        role="listitem"
        :options="filters.extensions"
        :title="$t('filters.extensions.title')"
        filter-type="extensions"
        @filterChanged="onUpdateFilter"
      />
      <FilterCheckList
        v-if="activeTab == 'image'"
        role="listitem"
        :options="filters.aspectRatios"
        :title="$t('filters.aspect-ratios.title')"
        filter-type="aspectRatios"
        @filterChanged="onUpdateFilter"
      />
      <FilterCheckList
        v-if="activeTab == 'image'"
        role="listitem"
        :options="filters.sizes"
        :title="$t('filters.sizes.title')"
        filter-type="sizes"
        @filterChanged="onUpdateFilter"
      />
      <div v-if="activeTab == 'image'" class="m-4 filter-option small-filter">
        <label for="creator" :aria-label="$t('browse-page.aria.creator')">
          <input
            id="creator"
            type="checkbox"
            :aria-label="$t('browse-page.aria.creator')"
            :checked="filters.searchBy.creator"
            @change="onUpdateSearchByCreator"
          />
          {{ $t('filters.creator.title') }}</label
        >
      </div>
    </form>
    <div
      v-if="isFilterApplied"
      class="m-6 pb-4 clear-filters hidden desk:block"
    >
      <button class="button tiny" @click="onClearFilters">
        {{ $t('filter-list.clear') }}
      </button>
    </div>
    <div v-if="isFilterApplied" class="bg-white p-6 desk:hidden text-center">
      <button class="button tiny mr-4" @click="onClearFilters">
        {{ $t('filter-list.clear') }}
      </button>
      <button
        class="button is-primary tiny"
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
  props: [
    'filters',
    'isFilterApplied',
    'licenseTypesDisabled',
    'licensesDisabled',
  ],
  computed: {
    activeTab() {
      return this.$route.path.split('search/')[1] || 'image'
    },
  },
  methods: {
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
</style>
