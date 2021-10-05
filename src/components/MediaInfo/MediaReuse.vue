<template>
  <section class="media-reuse">
    <h4 class="b-header mb-6">{{ $t('media-details.reuse.title') }}</h4>
    <div class="columns">
      <MediaLicense
        :license="media.license"
        :full-license-name="fullLicenseName"
        :license-url="licenseUrl"
        class="column"
      />
      <CopyLicense
        :media="media"
        :full-license-name="fullLicenseName"
        :license-url="licenseUrl"
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
    licenseUrl: String,
    fullLicenseName: String,
    attributionHtml: String,
  },
}
</script>
