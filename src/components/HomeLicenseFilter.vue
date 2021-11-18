<template>
  <fieldset class="home-license-filter mt-16">
    <legend class="w-full text-center">
      {{ $t('hero.license-filter.label') }}
    </legend>
    <template v-for="(licenseType, index) in filters">
      <label :key="index" class="checkbox mx-3" :for="licenseType.code">
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
