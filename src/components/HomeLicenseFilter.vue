<template>
  <fieldset class="home-license-filter mt-16">
    <legend>
      {{ $t('hero.license-filter.label') }}
    </legend>
    <template v-for="(licenseType, index) in licenseTypes">
      <label :key="index" class="checkbox" :for="licenseType.code">
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
import { mapActions, mapState } from 'vuex'
import { TOGGLE_FILTER } from '~/constants/action-types'

export default {
  name: 'LicenseFilter',
  computed: {
    ...mapState({
      licenseTypes: (state) => state.filters.licenseTypes,
    }),
  },
  methods: {
    ...mapActions({ toggleFilter: TOGGLE_FILTER }),
    onFilterChanged(code) {
      this.toggleFilter({
        code,
        filterType: 'licenseTypes',
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.home-license-filter {
  display: flex;
  justify-content: center;
  legend {
    display: flex;
    justify-content: center;
    width: 100%;
    margin-bottom: 0.5rem;
  }
}

.checkbox:not(:last-child) {
  margin-right: 1.5rem;
}
</style>
