<template>
  <section class="sidebar_section columns">
    <div
      v-if="fullLicenseName.includes('cc0') || fullLicenseName.includes('pdm')"
      class="photo-attribution column mb-6"
    >
      <h5 class="b-header mb-6">
        {{ $t('photo-details.reuse.tool-header') }}
      </h5>
      <LicenseExplanations :license="audio.license" />

      <i18n
        path="photo-details.reuse.tool.content"
        tag="span"
        class="caption font-semibold"
      >
        <template #link>
          <a
            :aria-label="$t('photo-details.aria.attribution.tool')"
            :href="licenseURL"
            target="_blank"
            rel="noopener"
          >
            {{ $t('photo-details.reuse.tool.link') }}
          </a>
        </template>
      </i18n>
    </div>
    <div v-else class="photo-attribution column mb-6">
      <h5 class="b-header mb-6">
        {{ $t('photo-details.reuse.license-header') }}
      </h5>
      <i18n
        ref="photoAttribution"
        path="photo-details.reuse.attribution.main"
        tag="span"
        class="photo_usage-attribution block"
      >
        <template #link>
          <a
            class="photo_license"
            :href="licenseURL"
            target="_blank"
            rel="noopener"
          >
            {{ fullLicenseName.toUpperCase() }}
          </a>
        </template>
      </i18n>

      <LicenseExplanations :license="audio.license" />

      <i18n
        path="photo-details.reuse.license.content"
        tag="span"
        class="caption font-semibold"
      >
        <template #link>
          <a
            :aria-label="$t('photo-details.aria.attribution.license')"
            :href="licenseURL"
            target="_blank"
            rel="noopener"
          >
            {{ $t('photo-details.reuse.license.link') }}
          </a>
        </template>
      </i18n>
    </div>
    <CopyAudioLicense
      :audio="audio"
      :full-license-name="fullLicenseName"
      :license-u-r-l="licenseURL"
      :attribution-html="attributionHtml"
    />
  </section>
</template>

<script>
export default {
  name: 'AudioAttribution',
  props: ['id', 'audio', 'ccLicenseURL', 'fullLicenseName', 'attributionHtml'],
  computed: {
    licenseURL() {
      return `${this.ccLicenseURL}&atype=rich`
    },
  },
}
</script>
