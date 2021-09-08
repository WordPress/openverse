<template>
  <section class="media-reuse">
    <h4 class="b-header mb-6">{{ $t('media-details.reuse.title') }}</h4>
    <div class="columns">
      <MediaLicense
        :license="media.license"
        :full-license-name="fullLicenseName"
        :license-u-r-l="licenseURL"
        class="column"
      />
      <CopyLicense
        :media="media"
        :full-license-name="fullLicenseName"
        :cc-license-u-r-l="ccLicenseURL"
        :attribution-html="attributionHtml"
        class="column"
      />
    </div>
  </section>
</template>

<script>
export default {
  name: 'MediaReuse',
  props: {
    media: {},
    ccLicenseURL: String,
    fullLicenseName: String,
    attributionHtml: String,
  },
  computed: {
    licenseURL() {
      return `${this.$props.ccLicenseURL}`
    },
  },
}
</script>
