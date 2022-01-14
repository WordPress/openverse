<template>
  <fieldset class="mb-8" @click.stop="hideLicenseExplanationVisibility">
    <legend v-if="title" class="text-2xl font-semibold mb-2">
      {{ title }}
    </legend>
    <div
      v-for="(item, index) in options"
      :key="index"
      class="flex justify-between items-center mt-3"
    >
      <VCheckbox
        :id="item.code"
        :key="index"
        :checked="item.checked"
        :name="itemName"
        :value="item.code"
        :disabled="isDisabled(item)"
        @change="onValueChange"
      >
        <VLicense v-if="filterType === 'licenses'" :license="item.code" />
        <template v-else>{{ itemLabel(item) }}</template>
      </VCheckbox>
      <button
        v-if="filterType === 'licenses'"
        :ref="`${item.code}licenseIcon`"
        :aria-label="$t('browse-page.aria.license-explanation')"
        class="appearance-none"
        type="button"
        @click.stop="toggleLicenseExplanationVisibility(item.code)"
      >
        <svg
          aria-hidden="true"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          class="pe-1"
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
    </div>
    <VLicenseExplanationTooltip
      v-if="licenseExplanationVisible"
      :license="licenseExplanationCode"
      :icon-dom-node="$refs[`${licenseExplanationCode}licenseIcon`][0]"
    />
  </fieldset>
</template>

<script>
import VLicenseExplanationTooltip from '~/components/VFilters/VLicenseExplanationTooltip'
import VCheckbox from '~/components/VCheckbox.vue'
import VLicense from '~/components/License/VLicense.vue'

export default {
  name: 'FilterCheckList',
  components: {
    VCheckbox,
    VLicense,
    VLicenseExplanationTooltip,
  },
  props: {
    options: { type: Array, required: false },
    title: { type: String },
    filterType: { type: String, required: true },
    disabled: { type: Boolean, default: false },
  },
  data() {
    return {
      licenseExplanationVisible: false,
      licenseExplanationCode: null,
    }
  },
  computed: {
    itemName() {
      return this.filterType === 'searchBy'
        ? this.$t('filters.searchBy.title')
        : this.title
    },
  },
  methods: {
    itemLabel(item) {
      return ['audioProviders', 'imageProviders'].includes(this.filterType)
        ? item.name
        : this.$t(item.name)
    },
    onValueChange({ value }) {
      this.$emit('filterChanged', {
        code: value,
        filterType: this.filterType,
      })
    },
    toggleLicenseExplanationVisibility(licenseCode) {
      this.licenseExplanationVisible = !this.licenseExplanationVisible
      this.licenseExplanationCode = licenseCode
    },
    hideLicenseExplanationVisibility() {
      this.licenseExplanationVisible = false
    },
    getFilterTypeValue(filterKey, val) {
      return this.$store.state.search.filters[filterKey].filter((item) =>
        item.code.includes(val)
      )
    },
    isDisabled(item) {
      if (this.filterType === 'licenseTypes') {
        const nc = this.getFilterTypeValue('licenses', 'nc')
        const nd = this.getFilterTypeValue('licenses', 'nd')
        return (
          (item.code === 'commercial' && nc.some((li) => li.checked)) ||
          (item.code === 'modification' && nd.some((li) => li.checked))
        )
      } else if (this.filterType === 'licenses') {
        const commercial = this.getFilterTypeValue('licenseTypes', 'commercial')
        const modification = this.getFilterTypeValue(
          'licenseTypes',
          'modification'
        )
        return (
          (commercial[0].checked && item.code.includes('nc')) ||
          (modification[0].checked && item.code.includes('nd'))
        )
      }
      return this.disabled
    },
    shouldRenderLicenseExplanationTooltip(licenseCode) {
      return (
        !this.isDisabled({ code: licenseCode }) &&
        this.licenseExplanationVisible &&
        this.licenseExplanationCode === licenseCode
      )
    },
  },
}
</script>
