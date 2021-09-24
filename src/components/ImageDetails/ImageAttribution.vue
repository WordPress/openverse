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
      :license-url="licenseUrl"
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
    openverseLicenseUrl: String,
    fullLicenseName: String,
    attributionHtml: String,
  },
  computed: {
    licenseUrl() {
      return `${this.openverseLicenseUrl}&atype=rich`
    },
  },
}
</script>
