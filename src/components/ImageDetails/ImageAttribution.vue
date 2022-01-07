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
import attributionHtml from '~/utils/attribution-html'
import CopyLicense from '~/components/MediaInfo/CopyLicense.vue'
import MediaLicense from '~/components/MediaInfo/MediaLicense.vue'

export default {
  name: 'ImageAttribution',
  components: {
    CopyLicense,
    MediaLicense,
  },
  props: {
    image: {
      type: Object,
    },
    licenseUrl: {
      type: String,
    },
    fullLicenseName: {
      type: String,
    },
  },
  computed: {
    licenseUrlRichText() {
      return `${this.licenseUrl}&atype=rich`
    },
    attributionHtml() {
      const licenseUrl = `${this.licenseUrl}&atype=html`
      return attributionHtml(this.image, licenseUrl, this.fullLicenseName)
    },
  },
}
</script>
