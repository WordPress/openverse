<template>
  <div class="social-share">
    <div class="share-list_social-items cell medium-6 large-4">
      <a
        class="social-button facebook"
        target="_blank"
        @click="onSocialMediaLinkClick('Facebook')"
        :href="`https://www.facebook.com/sharer/sharer.php?u=${shareURL}&description=${shareText}&href=${shareURL}`">
      </a>
      <a
        class="social-button twitter"
        target="_blank"
        @click="onSocialMediaLinkClick('Twitter')"
        :href="`https://twitter.com/intent/tweet?text=${shareText}`">
      </a>
      <a
        class="social-button pinterest"
        target="_blank"
        @click="onSocialMediaLinkClick('Pinterest')"
        :href="`https://www.pinterest.com/pin/create/bookmarklet/?media=${image_URL}&description=${shareText}`">
      </a>
    </div>
  </div>
</template>

<script>
import { SOCIAL_MEDIA_SHARE } from '@/store/action-types';
import { SEND_DETAIL_PAGE_EVENT, DETAIL_PAGE_EVENTS } from '@/store/usage-data-analytics-types';

export default {
  name: 'social-share-buttons',
  props: {
    shareURL: '',
    shareText: '',
    imageURL: '',
    image: {},
  },
  methods: {
    onSocialMediaLinkClick(site) {
      this.$store.dispatch(SOCIAL_MEDIA_SHARE, { site });
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.SHARED_SOCIAL,
        resultUuid: this.$props.image.id,
      });
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
