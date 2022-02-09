<template>
  <fieldset class="mb-8" @click.stop="hideLicenseExplanationVisibility">
    <legend v-if="title" class="text-sm font-semibold">
      {{ title }}
    </legend>
    <div
      v-for="(item, index) in options"
      :key="index"
      class="flex justify-between items-center mt-4"
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
        class="text-dark-charcoal-70 appearance-none"
        type="button"
        @click.stop="toggleLicenseExplanationVisibility(item.code)"
      >
        <VIcon :icon-path="helpIcon" />
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
import helpIcon from '~/assets/icons/help.svg'

import VLicenseExplanationTooltip from '~/components/VFilters/VLicenseExplanationTooltip.vue'
import VCheckbox from '~/components/VCheckbox/VCheckbox.vue'
import VLicense from '~/components/License/VLicense.vue'
import VIcon from '~/components/VIcon/VIcon.vue'

export default {
  name: 'FilterCheckList',
  components: {
    VCheckbox,
    VIcon,
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
      helpIcon,
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
