<template>
  <a :href="getLicenseURL(image)"
      @click.stop="() => false"
     class="photo-license-icons"
     target="_blank"
     rel="noopener noreferrer">
    <i class="icon cc-logo is-size-4 has-text-black has-background-white" title="CC">
    <!-- Closing i and opening template tag must be adjacent to prevent whitespace -->
    </i><template v-for="(license, index) in getLicenseIcon(image.license)">
      <i
          v-if="license"
          :class="{
            icon: true,
            ['has-text-black']: true,
            ['has-background-white']: true,
            ['is-size-4']: true,
            [`cc-${license}`]: true,
          }"
          :alt="`${license.toUpperCase()}`"
          :key="index" />
    </template>
  </a>
</template>

<script>

const APItoIconNameMap = {
  by: 'by',
  nc: 'nc',
  nd: 'nd',
  sa: 'sa',
  cc0: 'zero',
  pdm: 'pd',
};

const LicenseIcons = {
  name: 'license-icons',
  components: {},
  props: {
    image: '',
    shouldWrapInLink: false,
  },
  methods: {
    getLicenseIcon(license) {
      let licenses = [];
      if (license) {
        licenses = license.split('-');
      }
      return licenses.map(l => APItoIconNameMap[l]);
    },
    getLicenseURL(image) {
      if (!image) {
        return '';
      }

      const BASE_URL = 'https://creativecommons.org';
      let url = `${BASE_URL}/licenses/${image.license}/${image.license_version}`;
      let license = '';

      if (image.license) {
        license = image.license;
      }

      if (license === 'cc0') {
        this.image.license_version = '1.0';
        url = `${BASE_URL}/publicdomain/zero/1.0/`;
      }
      else if (image.license === 'pdm') {
        url = `${BASE_URL}/publicdomain/mark/1.0/`;
      }

      return url;
    },
  },
};

export default LicenseIcons;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .icon {
    vertical-align: middle;
    margin-right: .3rem;
  }
</style>
