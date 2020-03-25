<template>
  <div class="caption">
    <div v-if="status == 'NOT_SENT'">
      <span>Are these results relevant?</span>
      <button class="button is-text tiny is-paddingless rating is-shadowless"
              @click="sendSearchRatingEvent(true)">
        Yes
      </button>
      •
      <button class="button is-text tiny is-paddingless rating is-shadowless"
              @click="sendSearchRatingEvent(false)">
        No
      </button>
    </div>
    <div v-else-if="status == 'SENT'">
      <span class="thank-you">Thank you for the feedback!</span>
    </div>
  </div>
</template>

<script>
import { SEND_SEARCH_RATING_EVENT } from '@/store/usage-data-analytics-types';

const Statuses = {
  NOT_SENT: 'NOT_SENT',
  SENT: 'SENT',
};

export default {
  name: 'search-rating',
  props: ['searchTerm'],
  data() {
    return {
      status: Statuses.NOT_SENT,
    };
  },
  methods: {
    sendSearchRatingEvent(isRelevant) {
      this.$store.dispatch(SEND_SEARCH_RATING_EVENT, {
        query: this.$props.searchTerm,
        relevant: isRelevant,
      });

      this.status = Statuses.SENT;
      setTimeout(() => { this.status = null; }, 1500);
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@creativecommons/vocabulary/scss/color.scss";

.rating {
  vertical-align: middle;
  color: $color-dark-turquoise;
  font-size: 0.8rem;
  text-decoration: none;

  &:hover {
    background: none;
  }

  &:focus {
    background: none;
  }
}
</style>
