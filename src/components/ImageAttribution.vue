<template>
  <div class="photo-attribution">
    <p class="photo_usage-attribution" ref="photoAttribution">
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
  </div>
</template>

<script>
import LicenseIcons from '@/components/LicenseIcons';

export default {
  name: 'image-attribution',
  props: ['image', 'ccLicenseURL', 'fullLicenseName'],
  components: {
    LicenseIcons,
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
