<template>
  <span class="photo-license-icons">
    <i
      class="icon cc-logo text-lgr text-black has-background-white filter-icon"
      title="CC"
    >
      <!-- Closing i and opening template tag must be adjacent to prevent whitespace --> </i
    ><template v-for="(l, i) in getLicenseIcon(license)">
      <i
        v-if="l"
        :key="i"
        :class="{
          icon: true,
          ['text-black']: true,
          ['has-background-white']: true,
          ['text-lgr']: true,
          [`cc-${l}`]: true,
          ['filter-icon']: true,
        }"
        :alt="`${l.toUpperCase()}`"
      />
    </template>
  </span>
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

const LicenseIcons = {
  name: 'license-icons',
  props: {
    license: '',
  },
  methods: {
    getLicenseIcon(license) {
      let licenses = []
      if (license) {
        licenses = license.split('-')
      }
      return licenses.map((l) => APItoIconNameMap[l])
    },
  },
}

export default LicenseIcons
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.icon {
  vertical-align: middle;
  margin-right: 0.3rem;
}
.photo-license-icons {
  display: inline-block;
  margin-right: 0.188rem;
}
</style>
