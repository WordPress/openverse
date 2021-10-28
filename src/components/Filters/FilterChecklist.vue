<template>
  <div
    :class="{ ['filters']: true, ['single']: isSingleFilter, 'mb-8': true }"
    @click="hideLicenseExplanationVisibility()"
    @keyup.enter="hideLicenseExplanationVisibility()"
  >
    <div
      v-if="title"
      class="filters-title"
      @click.prevent="toggleFilterVisibility"
      @keyup.enter="toggleFilterVisibility"
    >
      <h4 class="filter-heading">{{ title }}</h4>
      <button
        v-if="!filtersExpandedByDefault"
        :aria-label="$t('filter-list.category-aria', { categoryName: title })"
        class="filter-visibility-toggle is-white py-2"
      >
        <i
          v-if="areFiltersExpanded"
          class="icon angle-up rotImg text-lg text-light-gray"
          title="toggle filters visibility"
        />
        <i
          v-else
          class="icon angle-down text-lg text-light-gray"
          title="toggle filters visibility"
        />
      </button>
    </div>
    <template v-if="areFiltersExpanded">
      <div
        v-for="(item, index) in options"
        :key="index"
        class="filter-checkbox-wrapper"
      >
        <!--eslint-disable vuejs-accessibility/label-has-for -->
        <label class="checkbox" :disabled="isDisabled(item)">
          <input
            :key="index"
            :name="item.code"
            type="checkbox"
            class="filter-checkbox mr-2"
            :checked="item.checked"
            :disabled="isDisabled(item)"
            @change="onValueChange"
          />
          <LicenseIcons v-if="filterType === 'licenses'" :license="item.code" />
          {{ itemLabel(item) }}
        </label>
        <button class="appearance-none" type="button">
          <svg
            v-if="filterType === 'licenses'"
            :ref="`${index}licenseIcon`"
            width="24"
            height="20"
            viewBox="0 0 24 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            :aria-label="$t('browse-page.aria.license-explanation')"
            tabindex="0"
            alt="help"
            class="license-help pr-1"
            @click.stop="toggleLicenseExplanationVisibility(item.code)"
            @keyup.enter="toggleLicenseExplanationVisibility(item.code)"
          >
            <circle cx="12" cy="10" r="8" stroke="#1E1E1E" stroke-width="1.5" />
            <path
              d="M9.75 8.25C9.75 7.00736 10.7574 6 12 6C13.2426 6 14.25 7.00736 14.25 8.25C14.25 9.40828 13.3748 10.3621 12.2496 10.4863C12.1124 10.5015 12 10.6119 12 10.75V12"
              stroke="#1E1E1E"
              stroke-width="1.5"
            />
            <path d="M12 13V14.5" stroke="#1E1E1E" stroke-width="1.5" />
          </svg>
        </button>

        <LicenseExplanationTooltip
          v-if="
            shouldRenderLicenseExplanationTooltip(item.code) &&
            !isDisabled(item)
          "
          :license="licenseExplanationCode"
          :icon-dom-node="$refs[`${index}licenseIcon`][0]"
        />
      </div>
    </template>
  </div>
</template>

<script>
import LicenseIcons from '~/components/LicenseIcons'
import LicenseExplanationTooltip from '~/components/Filters/LicenseExplanationTooltip'

export default {
  name: 'FilterCheckList',
  components: {
    LicenseIcons,
    LicenseExplanationTooltip,
  },
  props: ['options', 'title', 'filterType', 'disabled'],
  data() {
    return {
      filtersVisible: false,
      licenseExplanationVisible: false,
      licenseExplanationCode: '',
    }
  },
  computed: {
    /**
     * Show filters expanded by default
     * @todo: The A/B test is over and we're going with the expanded view. Can remove a lot of this old test logic
     */
    filtersExpandedByDefault() {
      return true
    },
    areFiltersExpanded() {
      return this.filtersExpandedByDefault || this.filtersVisible
    },
    isSingleFilter() {
      return this.$props.filterType === 'searchBy'
    },
  },
  methods: {
    itemLabel(item) {
      return ['audioProviders', 'imageProviders'].includes(
        this.$props.filterType
      )
        ? item.name
        : this.$t(item.name)
    },
    onValueChange(e) {
      this.$emit('filterChanged', {
        code: e.target.name,
        filterType: this.$props.filterType,
      })
    },
    /**
     * This function is used to hide sub items in filters
     * It was decided not to use them after a/b tests
     * TODO: either remove or use if necessary when implementing new designs
     */
    toggleFilterVisibility() {
      this.filtersVisible = !this.filtersVisible
    },
    toggleLicenseExplanationVisibility(licenseCode) {
      this.licenseExplanationVisible = !this.licenseExplanationVisible
      this.licenseExplanationCode = licenseCode
    },
    hideLicenseExplanationVisibility() {
      this.licenseExplanationVisible = false
    },
    getFilterTypeValue(filterKey, val) {
      return this.$store.state.filter.filters[filterKey].filter((item) =>
        item.code.includes(val)
      )
    },
    isDisabled(item) {
      if (this.$props.filterType === 'licenseTypes') {
        const nc = this.getFilterTypeValue('licenses', 'nc')
        const nd = this.getFilterTypeValue('licenses', 'nd')
        return (
          (item.code === 'commercial' && nc.some((li) => li.checked)) ||
          (item.code === 'modification' && nd.some((li) => li.checked))
        )
      }
      if (this.$props.filterType === 'licenses') {
        const commercial = this.getFilterTypeValue('licenseTypes', 'commercial')
        const modification = this.getFilterTypeValue(
          'licenseTypes',
          'modification'
        )
        return (
          (commercial.checked && item.code.includes('nc')) ||
          (modification.checked && item.code.includes('nd'))
        )
      }
      return this.$props.disabled
    },
    shouldRenderLicenseExplanationTooltip(licenseCode) {
      return (
        this.licenseExplanationVisible &&
        this.licenseExplanationCode === licenseCode
      )
    },
  },
}
</script>

<style lang="scss" scoped>
.filters-title {
  font-size: 1.25em;
  font-weight: 600;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.5;
  letter-spacing: normal;
  cursor: pointer;
  margin-bottom: 0.5rem;
}

.filter-heading {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.filter-visibility-toggle {
  float: right;
  cursor: pointer;
  background: none;
  border: none;
}

label {
  color: #333333;
}

.license-help {
  cursor: pointer;
  padding: 0;
}

.filter-checkbox-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.8rem;
}

.checkbox {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 500;
}
.checkbox input {
  min-width: 1.25rem;
  height: 1.25rem;
}

.single .checkbox {
  font-size: 0.875rem;
}
</style>
