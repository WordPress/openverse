<template>
  <div
    class="filters padding-vertical-big padding-left-big padding-right-normal"
    @click="hideLicenseExplanationVisibility()"
    @keyup.enter="hideLicenseExplanationVisibility()"
  >
    <div
      class="filters-title"
      @click.prevent="toggleFilterVisibility"
      @keyup.enter="toggleFilterVisibility"
    >
      <span>{{ title }}</span>
      <button
        v-if="!filtersExpandedByDefault"
        :aria-label="'filters list for' + title + 'category'"
        class="filter-visibility-toggle is-white padding-vertical-small"
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
    <template v-if="areFiltersExpanded && options">
      <div
        v-for="(item, index) in options"
        :key="index"
        class="margin-top-small filter-checkbox-wrapper"
      >
        <label class="checkbox" :for="item.code" :disabled="block(item)">
          <input
            :id="item.code"
            :key="index"
            type="checkbox"
            class="filter-checkbox margin-right-small"
            :checked="item.checked"
            :disabled="block(item)"
            @change="onValueChange"
          />
          <LicenseIcons v-if="filterType == 'licenses'" :license="item.code" />
          <template v-if="['providers', 'searchBy'].includes(filterType)">
            {{ item.name }}
          </template>
          <template v-else>
            {{ $t(item.name) }}
          </template>
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
            shouldRenderLicenseExplanationTooltip(item.code) && !block(item)
          "
          :license="licenseExplanationCode"
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
  props: ['options', 'title', 'filterType', 'disabled', 'checked'],
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
    block(e) {
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
</style>
