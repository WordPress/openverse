<template>
  <section class="sidebar_section social-sharing">
    <header class="sidebar_section-header">
      <h2>
        Share
      </h2>
    </header>
    <social-share-buttons
      :shareURL="shareURL"
      :imageURL="imageURL"
      :shareText="shareText">
    </social-share-buttons>
  </section>
</template>

<script>
import SocialShareButtons from '@/components/SocialShareButtons';

export default {
  name: 'image-social-share',
  props: ['image'],
  components: {
    SocialShareButtons,
  },
  computed: {
    shareURL() {
      return window.location.href;
    },
    imageURL() {
      return this.image.foreign_landing_url;
    },
    shareText() {
      return encodeURI(`I found an image through CC search @creativecommons: ${this.imageURL}`);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
