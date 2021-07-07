<template>
  <fieldset class="home-license-filter margin-top-xl">
    <legend class="is-block margin-bottom-small has-text-weight-medium">
      {{ $t('hero.license-filter.label') }}
    </legend>
    <template v-for="(licenseType, index) in licenseTypes">
      <label
        :key="index"
        class="checkbox margin-right-big"
        :for="licenseType.code"
      >
        <input
          :id="licenseType.code"
          type="checkbox"
          :checked="licenseType.checked"
          name="lt"
          :value="licenseType.code"
          @change="onFilterChanged(licenseType.code)"
        />
        {{ $t(licenseType.name) }}
      </label>
    </template>
  </fieldset>
</template>

<script>
import { TOGGLE_FILTER } from '~/store-modules/action-types'

export default {
  name: 'LicenseFilter',
  computed: {
    licenseTypes() {
      return this.$store.state.filters.licenseTypes
    },
  },
  methods: {
    onFilterChanged(code) {
      this.$store.dispatch(TOGGLE_FILTER, {
        code,
        filterType: 'licenseTypes',
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.home-license-filter {
  text-align: left;
  text-align: center;
}
span {
  display: block;
  font-size: 1.25em;
  font-weight: 600;
}
.license-filters {
  display: inline-block;
}
</style>
