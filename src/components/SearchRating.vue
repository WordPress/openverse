<template>
  <div class="caption">
    <span>Are these results relevant?:</span>
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
</template>

<script>
import { SEND_SEARCH_RATING_EVENT } from '@/store/usage-data-analytics-types';

export default {
  name: 'search-rating',
  props: ['searchTerm'],
  methods: {
    sendSearchRatingEvent(isRelevant) {
      this.$store.dispatch(SEND_SEARCH_RATING_EVENT, {
        query: this.$props.searchTerm,
        relevant: isRelevant,
      });
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
