<template>
  <span class="license-icons">
    <img class="photo_license-icon" src="@/assets/cc_icon.svg">
    <img  v-for="(license, index) in onGetLicenseIcon(license)"
          v-if="license" class="photo_license-icon"
          :src="require(`@/assets/cc-${license.toLowerCase()}_icon.svg`)"
          :key="index">
  </span>
</template>

<script>
const LicenseIcons = {
  name: 'license-icons',
  components: {},
  props: {
    license: '',
  },
  data: () => ({
    isLicenseIcons: false,
  }),
  methods: {
    onGetLicenseIcon(license) {
      let licenses = [];
      if (license) {
        licenses = license.split('-');
      }
      return licenses;
    },
  },
};

export default LicenseIcons;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .photo_license {
    text-transform: uppercase;
  }

  .photo_license-icons {
    display: block;
    whitespace: none;
  }

  .photo_license-icon {
    height: 32px;
  }
</style>
