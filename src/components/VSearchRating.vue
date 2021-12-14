<template>
  <div>
    <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
    <template v-if="status === 'NOT_SENT'">
      <span>{{ $t('browse-page.search-rating.content') }}</span>
      <button
        :aria-label="$t('browse-page.aria.relevance.yes')"
        class="button is-text tiny p-0 rating rating-yes"
        @click="sendSearchRatingEvent(true)"
        @keyup.enter="sendSearchRatingEvent(true)"
      >
        {{ $t('browse-page.search-rating.yes') }}
      </button>
      •
      <button
        :aria-label="$t('browse-page.aria.relevance.no')"
        class="button is-text tiny p-0 rating rating-no"
        @click="sendSearchRatingEvent(false)"
        @keyup.enter="sendSearchRatingEvent(false)"
      >
        {{ $t('browse-page.search-rating.no') }}
      </button>
    </template>
    <template v-else-if="status === 'SENT'">
      <span class="thank-you">{{
        $t('browse-page.search-rating.feedback-thanks')
      }}</span>
    </template>
  </div>
</template>

<script>
import { SEND_SEARCH_RATING_EVENT } from '~/constants/usage-data-analytics-types'
import { USAGE_DATA } from '~/constants/store-modules'

const Statuses = {
  NOT_SENT: 'NOT_SENT',
  SENT: 'SENT',
}

export default {
  name: 'VSearchRating',
  props: ['searchTerm'],
  data() {
    return {
      status: Statuses.NOT_SENT,
    }
  },
  methods: {
    sendSearchRatingEvent(isRelevant) {
      this.$store.dispatch(`${USAGE_DATA}/${SEND_SEARCH_RATING_EVENT}`, {
        query: this.$props.searchTerm,
        relevant: isRelevant,
      })

      this.status = Statuses.SENT
      setTimeout(() => {
        this.status = null
      }, 1500)
    },
  },
}
</script>

<style lang="scss" scoped>
.button.rating {
  vertical-align: middle;
  color: $color-transition-blue;
  font-size: 0.8rem;
  text-decoration: none;
  text-transform: none;

  &:hover {
    background: none;
  }

  &:focus {
    background: none;
  }
}

span {
  vertical-align: middle;
}
</style>
