<template>
  <div
    :class="{ ['filters']: true, ['single']: isSingleFilter }"
    @click="hideLicenseExplanationVisibility()"
    @keyup.enter="hideLicenseExplanationVisibility()"
  >
    <h4 v-if="title">{{ title }}</h4>

    <div
      v-for="(item, index) in options"
      :key="index"
      class="margin-top-small filter-checkbox-wrapper"
    >
      <label class="checkbox" :for="item.code" :disabled="isDisabled(item)">
        <input
          :key="index"
          :name="item.code"
          type="checkbox"
          class="filter-checkbox margin-right-small"
          :checked="item.checked"
          :disabled="isDisabled(item)"
          @change="onValueChange"
        />
        <LicenseIcons v-if="filterType == 'licenses'" :license="item.code" />
        {{ itemLabel(item) }}
      </label>
      <img
        v-if="filterType == 'licenses'"
        :aria-label="$t('browse-page.aria.license-explanation')"
        tabindex="0"
        src="@/assets/help_icon.svg"
        alt="help"
        class="license-help padding-top-smallest padding-right-smaller"
        @click.stop="toggleLicenseExplanationVisibility(item.code)"
        @keyup.enter="toggleLicenseExplanationVisibility(item.code)"
      />

      <LicenseExplanationTooltip
        v-if="
          shouldRenderLicenseExplanationTooltip(item.code) && !isDisabled(item)
        "
        :license="licenseExplanationCode"
      />
    </div>
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
  props: ['options', 'title', 'filterType'],
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
    isSingleFilter() {
      return this.filterType == 'searchBy'
    },
  },
  methods: {
    itemLabel(item) {
      return this.filterType == 'providers' ? item.name : this.$t(item.name)
    },
    onValueChange(e) {
      this.$emit('filterChanged', {
        code: e.target.name,
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
    isDisabled(e) {
      if (this.$props.filterType === 'licenseTypes') {
        const nc = this.$store.state.filters.licenses.filter((item) =>
          item.code.includes('nc')
        )
        const nd = this.$store.state.filters.licenses.filter((item) =>
          item.code.includes('nd')
        )
        return (
          (e.code === 'commercial' && nc.some((li) => li.checked)) ||
          (e.code === 'modification' && nd.some((li) => li.checked))
        )
      }

      if (this.$props.filterType === 'licenses') {
        const commercial = this.$store.state.filters.licenseTypes.find(
          (item) => item.code === 'commercial'
        )
        const modification = this.$store.state.filters.licenseTypes.find(
          (item) => item.code === 'modification'
        )
        return (
          (commercial.checked && e.code.includes('nc')) ||
          (modification.checked && e.code.includes('nd'))
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
.filters {
  border-bottom: 2px solid rgb(245, 245, 245);
  padding: 1.5rem 1rem 1.5rem 1.5rem;
  &.single {
    padding-left: 1rem;
  }
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

.filter-checkbox-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox {
  display: flex;
  margin-bottom: 0.75rem;
  align-items: center;
  font-size: 14px;
}
.single .checkbox {
  font-size: 1rem;
}
</style>
