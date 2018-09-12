<template>
  <div class="social-share">
    <div class="share-list_social-items cell medium-6 large-4">
      <a class="social-button facebook"
         target="_blank"
         :href="`https://www.facebook.com/sharer/sharer.php?u=${this.getShareListURL()}
          &t==${shareText}&href=${this.getShareListURL()}`"></a>
      <a class="social-button twitter"
         target="_blank"
         :href="`https://twitter.com/intent/tweet?text=${shareText}`"
      ></a>
      <a class="social-button pinterest"
         target="_blank"
         :href="`https://www.pinterest.com/pin/create/bookmarklet/?media=${images[0].url}&description=${getShareText()}`"></a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'social-share-list',
  props: {
    shareListURL: '',
    shareText: '',
  },
  computed: {
    getShareText() {
      return encodeURI(`I created an image list @creativecommons: ${this.shareListURL}`);
    },
    getShareListURL() {
      return this.$store.state.shareListURL;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  @import '../../node_modules/foundation-sites/scss/foundation';

  $social-button-size: 3.125rem;
  $social-button-border-width: 0.125rem;
  $social-button-font-size: 1.5625rem;
  $social-button-line-height: 2em;
  $social-button-border-radius: 1.6875rem;
  $social-button-transition: all 0.5s ease;
  $social-button-margin: 0.25rem;

  $social-brand-facebook: #3b5998;
  $social-brand-twitter: #55acee;
  $social-brand-pinterest: #c32aa3;

  @mixin social-button($brand-color, $brand-icon) {
    background: $brand-color;

    &:before {
      background: url( '../assets/#{$brand-icon}');
      content: '';
      width: 24px;
      height: 24px;
      display: inline-block;
    }
  }

  .share-list_social-items {
    .social-button {
      display: inline-block;
      position: relative;
      cursor: pointer;
      width: $social-button-size;
      height: $social-button-size;
      border: $social-button-border-width solid transparent;
      padding: 0;
      text-decoration: none;
      text-align: center;
      color: $white;
      font-size: $social-button-font-size;
      font-weight: normal;
      line-height: $social-button-line-height;
      border-radius: $social-button-border-radius;
      transition: $social-button-transition;
      margin-right: $social-button-margin;
      margin-bottom: $social-button-margin;

      &.facebook {
        @include social-button($social-brand-facebook, 'facebook-logo_white.svg')
      }

      &.twitter {
        @include social-button($social-brand-twitter, 'twitter-logo_white.svg')
      }

      &.pinterest {
        @include social-button($social-brand-pinterest, 'pinterest-logo_white.svg')
      }
    }
  }
</style>
