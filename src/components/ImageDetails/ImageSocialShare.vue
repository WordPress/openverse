<template>
  <section class="sidebar_section social-sharing">
    <SocialShareButtons
      :share-u-r-l="shareURL"
      :image-source-u-r-l="imageSourceURL"
      :image-u-r-l="imageURL"
      :share-text="shareText"
      :image="image"
    />
  </section>
</template>

<script>
import SocialShareButtons from './SocialShareButtons'

export default {
  name: 'ImageSocialShare',
  components: {
    SocialShareButtons,
  },
  props: ['image'],
  data: () => ({
    // for SSR, initiates it as an empty value
    shareURL: '',
  }),
  computed: {
    imageSourceURL() {
      return this.image.foreign_landing_url
    },
    imageURL() {
      return this.image.url
    },
    shareText() {
      return encodeURI(
        `I found an image through Openverse: ${this.imageSourceURL}`
      )
    },
  },
  mounted() {
    // for SSR, sets the value with window.location, which is only available on client
    this.shareURL = window.location.href
  },
}
</script>
