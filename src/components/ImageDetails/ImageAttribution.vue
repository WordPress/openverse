<template>
  <section class="sidebar_section">
    <div
      class="photo-attribution margin-bottom-big"
      v-if="fullLicenseName==='cc0 1.0' | fullLicenseName==='CC pdm 1.0'"
    >
      <h5 class="b-header margin-bottom-big">
        {{ $t('photo-details.reuse.license-header') }}
      </h5>
      This image was marked with<a
        class="photo_license"
        :href="licenseURL"
        target="_blank"
        rel="noopener"
      >
        {{ fullLicenseName.toUpperCase() }}
      </a>
      <license-explanations :license="image.license" />

      <i18n
        path="photo-details.reuse.license.content"
        tag="span"
        class="caption has-text-weight-semibold"
      >
        <template v-slot:link>
          <a
            aria-label="read more about the license"
            :href="licenseURL"
            target="_blank"
            rel="noopener"
          >
            {{ $t('photo-details.reuse.license.link') }}
          </a>
        </template>
      </i18n>
    </div>
    <div class="photo-attribution margin-bottom-big" v-else>
      <h5 class="b-header margin-bottom-big">
        {{ $t('photo-details.reuse.license-header') }}
      </h5>
      <i18n
        path="photo-details.reuse.attribution.main"
        tag="span"
        class="photo_usage-attribution is-block"
        ref="photoAttribution"
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
            aria-label="read more about the license"
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
        :fullLicenseName="fullLicenseName"
        :licenseURL="licenseURL"
        :attributionHtml="attributionHtml"
      />
    </div>
  </section>
</template>

<script>
import LicenseExplanations from '@/components/LicenseExplanations'
import CopyLicense from './CopyLicense'

export default {
  name: 'image-attribution',
  props: ['id', 'image', 'ccLicenseURL', 'fullLicenseName', 'attributionHtml'],
  components: {
    LicenseExplanations,
    CopyLicense,
  },
  computed: {
    licenseURL() {
      return `${this.ccLicenseURL}&atype=rich`
    },
  },
}
</script>
