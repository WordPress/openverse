<template>
  <section class="sidebar_section">
    <MediaLicense
      :full-license-name="fullLicenseName"
      :license="image.license"
      :license-url="licenseUrlRichText"
    />
    <CopyLicense
      :media="image"
      :full-license-name="fullLicenseName"
      :license-url="licenseUrlRichText"
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
    licenseUrl: String,
    fullLicenseName: String,
    attributionHtml: String,
  },
  computed: {
    licenseUrlRichText() {
      return `${this.licenseUrl}&atype=rich`
    },
  },
}
</script>
