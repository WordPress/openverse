<template>
  <fieldset class="home-license-filter mt-16 flex justify-center">
    <legend class="flex justify-center w-full mb-2">
      {{ $t('hero.license-filter.label') }}
    </legend>
    <VCheckbox
      v-for="[licenseType, isChecked] in Object.entries(filters)"
      :id="licenseType"
      :key="licenseType"
      class="me-6 last:me-0"
      :checked="isChecked"
      name="licenseType"
      @change="onFilterChanged"
    >
      {{ $t(`filters.license-types.${licenseType}`) }}
    </VCheckbox>
  </fieldset>
</template>

<script>
import VCheckbox from '~/components/VCheckbox'

export default {
  name: 'HomeLicenseFilter',
  components: { VCheckbox },
  props: {
    filters: {
      type: Object,
      required: true,
    },
  },
  methods: {
    onFilterChanged({ value, checked }) {
      this.$emit('toggle', { code: value, checked })
    },
  },
}
</script>
