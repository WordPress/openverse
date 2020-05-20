<template>
  <div class="filters padding-vertical-big padding-left-big padding-right-normal"
       @click="hideLicenseExplanationVisibility()">
    <div class="filters-title" @click.prevent="toggleFilterVisibility">
      <span>{{ title }}</span>
      <button class="filter-visibility-toggle is-white padding-vertical-small">
        <i v-if="filtersVisible"
           class="icon angle-up rotImg is-size-5 has-text-grey-light"
           title="toggle filters visibility" />
        <i v-else
           class="icon angle-down is-size-5 has-text-grey-light"
           title="toggle filters visibility" />
      </button>
    </div>
    <template v-if="filtersVisible && options">
    <div v-for="(item, index) in options" :key="index" class="margin-top-small">
      <label class="checkbox" :for="item.code">
        <input type="checkbox"
             class="filter-checkbox margin-right-small"
             :id="item.code"
             :key="index"
             :checked="item.checked"
             :disabled="disabled"
             @change="onValueChange" />
        <license-icons v-if="filterType == 'licenses'" :license="item.code" />
        {{ item.name }}
      </label>
      <img  v-if="filterType == 'licenses'"
            src="@/assets/help_icon.svg"
            alt="help"
            class="license-help is-pulled-right padding-top-smallest"
            @click.stop="toggleLicenseExplanationVisibility(item.code)" />

      <license-explanation-tooltip
        v-if="shouldRenderLicenseExplanationTooltip(item.code)"
        :license="licenseExplanationCode" />
    </div>
    </template>
    <template v-if="filtersVisible && filterType === 'mature'">
        <label class="checkbox margin-top-small" for="mature">
          <input id="mature"
                 class="filter-checkbox"
                 type="checkbox"
                 :checked="checked"
                 @change="onValueChange">
          Enable Mature Content
        </label>
    </template>
  </div>
</template>

<script>
import LicenseIcons from '@/components/LicenseIcons';
import LicenseExplanationTooltip from './LicenseExplanationTooltip';

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
    };
  },
  methods: {
    onValueChange(e) {
      this.$emit('filterChanged', { code: e.target.id, filterType: this.$props.filterType });
    },
    toggleFilterVisibility() {
      this.filtersVisible = !this.filtersVisible;
    },
    toggleLicenseExplanationVisibility(licenseCode) {
      this.licenseExplanationVisible = !this.licenseExplanationVisible;
      this.licenseExplanationCode = licenseCode;
    },
    hideLicenseExplanationVisibility() {
      this.licenseExplanationVisible = false;
    },
    shouldRenderLicenseExplanationTooltip(licenseCode) {
      return this.licenseExplanationVisible && this.licenseExplanationCode === licenseCode;
    },
  },
};
</script>

<style lang="scss" scoped>
.filters {
  border-bottom: 2px solid rgb(245, 245, 245);
}

.filters-title {
  font-size: 1.250em;
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
