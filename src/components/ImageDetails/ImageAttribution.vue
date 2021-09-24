<template>
  <section class="sidebar_section">
    <MediaLicense
      :full-license-name="fullLicenseName"
      :license="image.license"
      :license-u-r-l="licenseUrl"
    />
    <CopyLicense
      :media="image"
      :full-license-name="fullLicenseName"
      :license-u-r-l="licenseUrl"
      :attribution-html="attributionHtml"
      class="my-6"
    />
  </section>
</template>

<script>
export default {
  name: 'ImageAttribution',
  props: {
    id: {},
    image: {},
    ccLicenseUrl: String,
    fullLicenseName: String,
    attributionHtml: String,
  },
  computed: {
    licenseUrl() {
      return `${this.ccLicenseUrl}&atype=rich`
    },
  },
}
</script>
