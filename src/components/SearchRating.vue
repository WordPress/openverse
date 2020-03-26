<template>
  <div class="caption has-text-weight-semibold">
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
.rating {
  vertical-align: middle;
  color: rgb(5, 181, 218) !important;
  font-size: 0.8rem !important;
  text-decoration: none !important;
  text-transform: none !important;

  &:hover {
    background: none !important;
  }

  &:focus {
    background: none !important;
  }
}

span {
  vertical-align: middle;
}
</style>
