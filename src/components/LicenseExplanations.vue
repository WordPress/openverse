<template>
  <div v-if="license">
    <ul class="margin-vertical-small">
      <template v-for="(li, index) in splitLicenses">
        <li
          :key="index"
          :class="{
            ['margin-vertical-small']: true,
            ['is-flex']: true,
          }"
        >
          <i
            :class="{
              icon: true,
              ['text-black']: true,
              ['bg-white']: true,
              ['is-size-4']: true,
              ['margin-right-small']: true,
              [`cc-${getLicenseIcon(li)}`]: true,
            }"
            :alt="`${li.toUpperCase()}`"
          />
          <p>{{ getLicenseDescription(li) }}</p>
        </li>
      </template>
    </ul>
  </div>
</template>

<script>
const APItoIconNameMap = {
  by: 'by',
  nc: 'nc',
  nd: 'nd',
  sa: 'sa',
  cc0: 'zero',
  pdm: 'pd',
}

const LicenseExplanations = {
  name: 'license-explanations',
  components: {},
  props: {
    license: '',
  },
  computed: {
    splitLicenses() {
      return this.$props.license.split('-')
    },
    LicenseTermDescriptions() {
      return {
        by: this.$t('browse-page.license-description.by'),
        nc: this.$t('browse-page.license-description.nc'),
        nd: this.$t('browse-page.license-description.nd'),
        sa: this.$t('browse-page.license-description.sa'),
        cc0: this.$t('browse-page.license-description.cc0'),
        pdm: this.$t('browse-page.license-description.pdm'),
      }
    },
  },
  methods: {
    getLicenseIcon(licenseTerm) {
      return APItoIconNameMap[licenseTerm]
    },
    getLicenseDescription(licenseTerm) {
      return this.LicenseTermDescriptions[licenseTerm]
    },
  },
}

export default LicenseExplanations
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped></style>
