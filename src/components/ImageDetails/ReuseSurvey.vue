<template>
  <div class="reuse-survey caption has-text-weight-semibold">
    How are you using this image?
    <a :href="formLink" target="_blank" rel="noopener" @click="onReuseSurveyClick">
      Let us know
    </a>
    by answering a few questions.
  </div>
</template>

<script>
import { SEND_DETAIL_PAGE_EVENT, DETAIL_PAGE_EVENTS } from '@/store/usage-data-analytics-types';

export default {
  name: 'reuse-survey',
  props: ['image'],
  data: () => ({
    // for SSR, initiates it as an empty value
    location: '',
  }),
  computed: {
    formLink() {
      const location = this.location;
      return `https://docs.google.com/forms/d/e/1FAIpQLSeSApxNMup8Ujt-8Vjv53ngltzhJeaHspMykHCD8VKQ39yXAA/viewform?usp=pp_url&entry.1690035721=${location}`;
    },
  },
  mounted() {
    // for SSR, sets the value with window.location, which is only available on client
    this.location = window.location.href;
  },
  methods: {
    onReuseSurveyClick() {
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.REUSE_SURVEY,
        resultUuid: this.$props.image.id,
      });
    },
  },
};
</script>
