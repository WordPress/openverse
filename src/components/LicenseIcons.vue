<template>
  <span class="photo-license-icons">
    <i
      class="icon cc-logo is-size-4 has-text-black has-background-white"
      title="CC"
    >
      <!-- Closing i and opening template tag must be adjacent to prevent whitespace --> </i
    ><template v-for="(l, i) in getLicenseIcon(license)">
      <i
        v-if="l"
        :class="{
          icon: true,
          ['has-text-black']: true,
          ['has-background-white']: true,
          ['is-size-4']: true,
          [`cc-${l}`]: true,
        }"
        :alt="`${l.toUpperCase()}`"
        :key="i"
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
  components: {},
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
</style>
