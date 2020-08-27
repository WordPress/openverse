<template>
  <div>
    <div class="filterlist-header">
      <h4
        class="padding-top-big padding-left-big padding-right-normal is-inline-block"
      >
        {{ $t('filter-list.filter-by') }}
      </h4>

      <button
        type="button"
        class="button is-text tiny is-paddingless margin-top-big margin-right-small report is-shadowless is-pulled-right"
        @click="onToggleSearchGridFilter()"
        v-on:keyup.enter="onToggleSearchGridFilter()"
      >
        <span class="has-color-tomato is-hidden-touch">{{
          $t('filter-list.hide')
        }}</span>
        <span class="margin-right-normal is-size-5 is-hidden-desktop">
          <i class="icon cross" />
        </span>
      </button>
    </div>
    <form
      :class="{
        'filters-form': true,
      }"
      role="list"
    >
      <filter-check-list
        role="listitem"
        :options="filters.licenseTypes"
        :disabled="licenseTypesDisabled"
        :title="$t('filters.license-types.title')"
        filterType="licenseTypes"
        @filterChanged="onUpdateFilter"
      />
      <filter-check-list
        role="listitem"
        v-if="activeTab == 'image'"
        :options="filters.licenses"
        :disabled="licensesDisabled"
        :title="$t('filters.licenses.title')"
        filterType="licenses"
        @filterChanged="onUpdateFilter"
      />
      <filter-check-list
        role="listitem"
        v-if="activeTab == 'image'"
        :options="filters.providers"
        :title="$t('filters.providers.title')"
        filterType="providers"
        @filterChanged="onUpdateFilter"
      />
      <filter-check-list
        role="listitem"
        v-if="activeTab == 'image'"
        :options="filters.categories"
        :title="$t('filters.categories.title')"
        filterType="categories"
        @filterChanged="onUpdateFilter"
      />
      <filter-check-list
        role="listitem"
        v-if="activeTab == 'image'"
        :options="filters.extensions"
        :title="$t('filters.extensions.title')"
        filterType="extensions"
        @filterChanged="onUpdateFilter"
      />
      <filter-check-list
        role="listitem"
        v-if="activeTab == 'image'"
        :options="filters.aspectRatios"
        :title="$t('filters.aspect-ratios.title')"
        filterType="aspectRatios"
        @filterChanged="onUpdateFilter"
      />
      <filter-check-list
        role="listitem"
        v-if="activeTab == 'image'"
        :options="filters.sizes"
        :title="$t('filters.sizes.title')"
        filterType="sizes"
        @filterChanged="onUpdateFilter"
      />
      <div
        v-if="activeTab == 'image'"
        class="margin-normal filter-option small-filter margin-bottom-normal"
      >
        <label for="creator-chk" :aria-label="$t('browse-page.aria.creator')">
          <input
            id="creator-chk"
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
      class="margin-big padding-bottom-normal clear-filters is-hidden-touch"
      v-if="isFilterApplied"
    >
      <button
        class="button tiny"
        @click="onClearFilters"
        v-on:keyup.enter="onClearFilters"
      >
        {{ $t('filter-list.clear') }}
      </button>
    </div>
    <div
      v-if="isFilterApplied"
      class="has-background-white padding-big is-hidden-desktop has-text-centered"
    >
      <button
        class="button tiny margin-right-normal"
        @click="onClearFilters"
        v-on:keyup.enter="onClearFilters"
      >
        {{ $t('filter-list.clear') }}
      </button>
      <button
        class="button is-primary tiny"
        @click="onToggleSearchGridFilter()"
        v-on:keyup.enter="onToggleSearchGridFilter()"
      >
        {{ $t('filter-list.show') }}
      </button>
    </div>
  </div>
</template>

<script>
import { ExperimentData } from '@/abTests/experiments/filterExpansion'
import FilterCheckList from './FilterChecklist'

export default {
  name: 'filters-list',
  props: [
    'filters',
    'isFilterApplied',
    'licenseTypesDisabled',
    'licensesDisabled',
  ],
  components: {
    FilterCheckList,
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
  computed: {
    activeTab() {
      return this.$route.path.split('search/')[1] || 'image'
    },
    /**
     * Check if a filter experiment is active, and if the current case is 'expanded'.
     * Show filters collapsed by default
     */
    filtersExpandedByDefault() {
      const experiment = this.$store.state.experiments.find(
        (exp) => exp.name === ExperimentData.EXPERIMENT_NAME
      )
      return experiment
        ? experiment.case === ExperimentData.FILTERS_EXPANDED_CASE
        : false
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
