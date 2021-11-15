<template>
  <fieldset class="home-license-filter mt-16">
    <legend>
      {{ $t('hero.license-filter.label') }}
    </legend>
    <template v-for="(licenseType, index) in filters">
      <label :key="index" class="checkbox" :for="licenseType.code">
        <input
          :id="licenseType.code"
          v-model="licenseType.checked"
          type="checkbox"
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
export default {
  name: 'LicenseFilter',
  data: () => ({
    filters: [
      {
        code: 'commercial',
        name: 'filters.license-types.commercial',
        checked: false,
      },
      {
        code: 'modification',
        name: 'filters.license-types.modification',
        checked: false,
      },
    ],
  }),
  methods: {
    onFilterChanged(code) {
      this.$emit('toggle', { code })
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
