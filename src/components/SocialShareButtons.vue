<template>
  <div class="social-share">
    <h5 class="b-header margin-bottom-normal">Share</h5>
    <div class="share-list_social-items">
      <a
        class="social-button facebook"
        target="_blank"
        @click="onSocialMediaLinkClick('Facebook')"
        :href="`https://www.facebook.com/sharer/sharer.php?u=${shareURL}&description=${shareText}&href=${shareURL}`">
        <i class="icon facebook colored margin-right-normal is-size-1"></i>
      </a>
      <a
        class="social-button twitter"
        target="_blank"
        @click="onSocialMediaLinkClick('Twitter')"
        :href="`https://twitter.com/intent/tweet?text=${shareText}`">
        <i class="icon twitter colored margin-right-normal is-size-1" />
      </a>
      <a
        class="social-button pinterest"
        target="_blank"
        @click="onSocialMediaLinkClick('Pinterest')"
        :href="`https://www.pinterest.com/pin/create/bookmarklet/?media=${imageURL}&description=${shareText}`">
        <i class="icon pinterest colored is-size-1" />
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
    shareURL: { default: '' },
    shareText: { default: '' },
    imageURL: { default: '' },
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
