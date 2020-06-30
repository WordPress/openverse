<template>
  <section class="sidebar_section">
    <div class="photo-attribution margin-bottom-big">
      <h5 class="b-header margin-bottom-big">License</h5>
      <span class="photo_usage-attribution is-block" ref="photoAttribution">
        This image was marked with a
        <a class="photo_license" :href="licenseURL" target="_blank" rel="noopener">
        {{ fullLicenseName.toUpperCase() }}
        </a>
        license.
      </span>
      <license-explanations :license="image.license" />

      <span class="caption has-text-weight-semibold">
        Read more about the license
        <a :href="licenseURL" target="_blank" rel="noopener">
        here
        </a>
      </span>
    </div>
    <div>
      <copy-license :image="image"
                    :fullLicenseName="fullLicenseName"
                    :licenseURL="licenseURL"
                    :attributionHtml="attributionHtml" />
    </div>
  </section>
</template>

<script>
import LicenseExplanations from '@/components/LicenseExplanations';
import CopyLicense from './CopyLicense';

export default {
  name: 'image-attribution',
  props: ['id', 'image', 'ccLicenseURL', 'fullLicenseName', 'attributionHtml'],
  components: {
    LicenseExplanations,
    CopyLicense,
  },
  computed: {
    licenseURL() {
      return `${this.ccLicenseURL}&atype=rich`;
    },
  },
};
</script>
