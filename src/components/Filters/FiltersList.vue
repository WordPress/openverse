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
        @keyup.enter="onToggleSearchGridFilter()"
      >
        <span
          class="has-color-transition-blue is-hidden-touch text-sm is-lowercase"
          >{{ $t('filter-list.hide') }}</span
        >
        <span class="margin-right-normal text-lg is-hidden-desktop">
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
      <div
        v-if="activeTab == 'image'"
        class="margin-normal filter-option small-filter margin-bottom-normal"
      >
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
      class="margin-big padding-bottom-normal clear-filters is-hidden-touch"
    >
      <button class="button tiny" @click="onClearFilters">
        {{ $t('filter-list.clear') }}
      </button>
    </div>
    <div
      v-if="isFilterApplied"
      class="bg-white padding-big is-hidden-desktop text-center"
    >
      <button class="button tiny margin-right-normal" @click="onClearFilters">
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
