<template>
  <div :class="{ 'social-share': true, 'social-share__medium': isMedium }">
    <div class="share-list_social-items cell medium-6 large-4">
      <a 
        class="social-button facebook"
        target="_blank"
        :href="`https://www.facebook.com/sharer/sharer.php?u=${shareURL}&t==${shareText}&href=${shareURL}`">
      </a>
      <a 
        class="social-button twitter"
        target="_blank"
        :href="`https://twitter.com/intent/tweet?text=${shareText}`">
      </a>
      <a 
        class="social-button pinterest"
        target="_blank"
        :href="`https://www.pinterest.com/pin/create/bookmarklet/?media=${imageURL}&description=${shareText}`">
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'social-share-list',
  props: {
    isMedium: '',  // Refers to slightly smaller sized version
    shareURL: '',
    shareText: '',
    imageURL: '',
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

  $social-brand-facebook: #4267b2;
  $social-brand-twitter: #1da1f2;
  $social-brand-pinterest: #e60023;

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

  .social-share{
    &__medium .social-button {
      width: $social-button-size / 1.5 !important;
      height: $social-button-size / 1.5 !important;
      font-size: $social-button-font-size / 2 !important;
      &:before {
        width: 12px;
        height: 12px;
      }
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
