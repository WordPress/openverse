<template>
  <div class="social-share">
    <div class="share-list_social-items">
      <a
        :aria-label="$t('photo-details.aria.share.facebook')"
        class="social-button facebook"
        target="_blank"
        @click="onSocialMediaLinkClick('Facebook')"
        v-on:keyup.enter="onSocialMediaLinkClick('Facebook')"
        :href="`https://www.facebook.com/sharer/sharer.php?u=${shareURL}&description=${shareText}&href=${shareURL}`"
      >
        <i class="icon facebook colored margin-right-normal is-size-1"></i>
      </a>
      <a
        :aria-label="$t('photo-details.aria.share.twitter')"
        class="social-button twitter"
        target="_blank"
        @click="onSocialMediaLinkClick('Twitter')"
        v-on:keyup.enter="onSocialMediaLinkClick('Twitter')"
        :href="`https://twitter.com/intent/tweet?text=${shareText}`"
      >
        <i class="icon twitter colored margin-right-normal is-size-1" />
      </a>
      <a
        :aria-label="$t('photo-details.aria.share.pinterest')"
        class="social-button pinterest"
        target="_blank"
        @click="onSocialMediaLinkClick('Pinterest')"
        v-on:keyup.enter="onSocialMediaLinkClick('Pinterest')"
        :href="`https://www.pinterest.com/pin/create/bookmarklet/?media=${imageURL}&description=${shareText}`"
      >
        <i class="icon pinterest colored is-size-1" />
      </a>
    </div>
  </div>
</template>

<script>
import { SOCIAL_MEDIA_SHARE } from '../store/action-types'
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '../store/usage-data-analytics-types'

export default {
  name: 'social-share-buttons',
  props: {
    shareURL: { default: '' },
    shareText: { default: '' },
    imageSourceURL: { default: '' },
    imageURL: { default: '' },
    image: {},
  },
  methods: {
    onSocialMediaLinkClick(site) {
      this.$store.dispatch(SOCIAL_MEDIA_SHARE, { site })
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.SHARED_SOCIAL,
        resultUuid: this.$props.image.id,
      })
    },
  },
}
</script>
