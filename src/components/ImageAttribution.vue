<template>
  <section class="sidebar_section">
    <header class="sidebar_section-header">
      <h2>
        Image Attribution
      </h2>
    </header>
    <div class="photo-attribution">
      <p id="attribution" class="photo_usage-attribution" ref="photoAttribution">
        <a :href="image.foreign_landing_url">"{{ image.title }}"</a>
        <span v-if="image.creator">
          by
          <a v-if="image.creator_url" :href="image.creator_url">{{ image.creator }}</a>
          <span v-else>{{ image.creator }}</span>
        </span>
        is licensed under
        <a class="photo_license" :href="ccLicenseURL">
        {{ fullLicenseName }}
        </a>
        <license-icons :image="image"></license-icons>
      </p>
      <CopyButton el="#attribution"
                  title="Can be used in WYSIWYG editors">
        Copy Attribution
      </CopyButton>
    </div>

    <div>
    </div>
  </section>
</template>

<script>
import LicenseIcons from '@/components/LicenseIcons';
import CopyButton from '@/components/CopyButton';

export default {
  name: 'image-attribution',
  props: ['id', 'image', 'ccLicenseURL', 'fullLicenseName'],
  components: {
    LicenseIcons,
    CopyButton,
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
