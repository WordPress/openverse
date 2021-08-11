<template>
  <div class="social-share">
    <div class="share-list_social-items">
      <a
        :aria-label="$t('photo-details.aria.share.facebook')"
        class="social-button facebook"
        target="_blank"
        :href="`https://www.facebook.com/sharer/sharer.php?u=${shareURL}&description=${shareText}&href=${shareURL}`"
        @click="onSocialMediaLinkClick('Facebook')"
        @keyup.enter="onSocialMediaLinkClick('Facebook')"
      >
        <i class="icon facebook colored mr-4 text-6xl" />
      </a>
      <a
        :aria-label="$t('photo-details.aria.share.twitter')"
        class="social-button twitter"
        target="_blank"
        :href="`https://twitter.com/intent/tweet?text=${shareText}`"
        @click="onSocialMediaLinkClick('Twitter')"
        @keyup.enter="onSocialMediaLinkClick('Twitter')"
      >
        <i class="icon twitter colored mr-4 text-6xl" />
      </a>
      <a
        :aria-label="$t('photo-details.aria.share.pinterest')"
        class="social-button pinterest"
        target="_blank"
        :href="`https://www.pinterest.com/pin/create/bookmarklet/?media=${imageURL}&description=${shareText}`"
        @click="onSocialMediaLinkClick('Pinterest')"
        @keyup.enter="onSocialMediaLinkClick('Pinterest')"
      >
        <i class="icon pinterest colored text-6xl" />
      </a>
    </div>
  </div>
</template>

<script>
import { SOCIAL_MEDIA_SHARE } from '~/store-modules/action-types'
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'

export default {
  name: 'SocialShareButtons',
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
