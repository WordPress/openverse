<template>
  <div
    class="filters padding-vertical-big padding-left-big padding-right-normal"
    @click="hideLicenseExplanationVisibility()"
  >
    <div class="filters-title" @click.prevent="toggleFilterVisibility">
      <span>{{ title }}</span>
      <button
        v-if="!filtersExpandedByDefault"
        class="filter-visibility-toggle is-white padding-vertical-small"
      >
        <i
          v-if="areFiltersExpanded"
          class="icon angle-up rotImg is-size-5 has-text-grey-light"
          title="toggle filters visibility"
        />
        <i
          v-else
          class="icon angle-down is-size-5 has-text-grey-light"
          title="toggle filters visibility"
        />
      </button>
    </div>
    <template v-if="areFiltersExpanded && options">
      <div
        v-for="(item, index) in options"
        :key="index"
        class="margin-top-small"
      >
        <label class="checkbox" :for="item.code">
          <input
            type="checkbox"
            class="filter-checkbox margin-right-small"
            :id="item.code"
            :key="index"
            :checked="item.checked"
            :disabled="disabled"
            @change="onValueChange"
          />
          <license-icons v-if="filterType == 'licenses'" :license="item.code" />
          {{ item.name }}
        </label>
        <img
          v-if="filterType == 'licenses'"
          src="@/assets/help_icon.svg"
          alt="help"
          class="license-help is-pulled-right padding-top-smallest padding-right-smaller"
          @click.stop="toggleLicenseExplanationVisibility(item.code)"
        />

        <license-explanation-tooltip
          v-if="shouldRenderLicenseExplanationTooltip(item.code)"
          :license="licenseExplanationCode"
        />
      </div>
    </template>
  </div>
</template>

<script>
import findIndex from 'lodash.findindex'
import { ExperimentData } from '@/abTests/filterVisibilityExperiment'
import LicenseIcons from '@/components/LicenseIcons'
import LicenseExplanationTooltip from './LicenseExplanationTooltip'

export default {
  name: 'filter-check-list',
  components: {
    LicenseIcons,
    LicenseExplanationTooltip,
  },
  props: ['options', 'title', 'filterType', 'disabled', 'checked'],
  data() {
    return {
      filtersVisible: false,
      licenseExplanationVisible: false,
      licenseExplanationCode: '',
    }
  },
  computed: {
    filtersExpandedByDefault() {
      const idx = findIndex(
        this.$store.state.experiments,
        (exp) => exp.name === ExperimentData.EXPERIMENT_NAME
      )

      if (idx >= 0) {
        const experiment = this.$store.state.experiments[idx]
        return experiment.case === ExperimentData.FILTERS_EXPANDED_EXPERIMENT
      }
      return false
    },
    areFiltersExpanded() {
      return this.filtersExpandedByDefault || this.filtersVisible
    },
  },
  methods: {
    onValueChange(e) {
      this.$emit('filterChanged', {
        code: e.target.id,
        filterType: this.$props.filterType,
      })
    },
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
.filters {
  border-bottom: 2px solid rgb(245, 245, 245);
}

.filters-title {
  font-size: 1.25em;
  font-weight: 600;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.5;
  letter-spacing: normal;
  cursor: pointer;
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
}
</style>
