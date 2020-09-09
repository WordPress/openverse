<template>
  <section class="sidebar_section">
    <div
      v-if="fullLicenseName.includes('cc0') || fullLicenseName.includes('pdm')"
      class="photo-attribution margin-bottom-big"
    >
      <h5 class="b-header margin-bottom-big">
        {{ $t('photo-details.reuse.tool-header') }}
      </h5>
      <license-explanations :license="image.license" />

      <i18n
        path="photo-details.reuse.tool.content"
        tag="span"
        class="caption has-text-weight-semibold"
      >
        <template v-slot:link>
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
    <div v-else class="photo-attribution margin-bottom-big">
      <h5 class="b-header margin-bottom-big">
        {{ $t('photo-details.reuse.license-header') }}
      </h5>
      <i18n
        ref="photoAttribution"
        path="photo-details.reuse.attribution.main"
        tag="span"
        class="photo_usage-attribution is-block"
      >
        <template v-slot:link>
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

      <license-explanations :license="image.license" />

      <i18n
        path="photo-details.reuse.license.content"
        tag="span"
        class="caption has-text-weight-semibold"
      >
        <template v-slot:link>
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
    <div>
      <copy-license
        :image="image"
        :full-license-name="fullLicenseName"
        :license-u-r-l="licenseURL"
        :attribution-html="attributionHtml"
      />
    </div>
  </section>
</template>

<script>
import LicenseExplanations from '@/components/LicenseExplanations'
import CopyLicense from './CopyLicense'

export default {
  name: 'ImageAttribution',
  components: {
    LicenseExplanations,
    CopyLicense,
  },
  props: ['id', 'image', 'ccLicenseURL', 'fullLicenseName', 'attributionHtml'],
  computed: {
    licenseURL() {
      return `${this.ccLicenseURL}&atype=rich`
    },
  },
}
</script>
