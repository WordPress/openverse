<template>
  <section>
    <div v-show="!fetchingState.isFetching" class="results-meta">
      <span class="caption font-semibold">
        {{ _audiosCount }}
      </span>
    </div>
    <div class="px-6 pt-6">
      <AudioTrack
        v-for="audio in results.items"
        :key="audio.id"
        :audio="audio"
        :size="audioTrackSize"
        layout="row"
      />
    </div>
    <div v-if="!fetchingState.fetchingError" class="load-more">
      <button
        v-show="!fetchingState.isFetching"
        class="button"
        :disabled="isFinished"
        @click="onLoadMoreAudios"
        @keyup.enter="onLoadMoreAudios"
      >
        <span v-if="isFinished">{{
          $t('browse-page.no-more', {
            type: $t('browse-page.search-form.audio'),
          })
        }}</span>
        <span v-else>{{ $t('browse-page.load') }}</span>
      </button>
      <LoadingIcon v-show="fetchingState.isFetching" />
    </div>
    <div
      v-if="fetchingState.fetchingError"
      class="m-auto w-1/2 text-center pt-6"
    >
      <h5>
        {{
          $t('browse-page.fetching-error', {
            type: $t('browse-page.search-form.audio'),
          })
        }}
        {{ fetchingState.fetchingError }}
      </h5>
    </div>
  </section>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import { FETCH_MEDIA } from '~/constants/action-types'
import { AUDIO } from '~/constants/media'
import { MEDIA, SEARCH } from '~/constants/store-modules'

export default {
  name: 'AudioResultsList',
  async fetch() {
    if (!this.results.items.length) {
      await this.fetchMedia({
        ...this.query,
        mediaType: AUDIO,
      })
    }
  },
  computed: {
    ...mapState(SEARCH, ['query', 'isFilterVisible']),
    ...mapGetters(MEDIA, ['fetchingState', 'results', 'isFinished']),
    _audiosCount() {
      const count = this.results.count
      if (count === 0) {
        return this.$t('browse-page.audio-no-results')
      }
      const localeCount = count.toLocaleString(this.$i18n.locale)
      const i18nKey =
        count >= 10000
          ? 'browse-page.audio-result-count-more'
          : 'browse-page.audio-result-count'
      return this.$tc(i18nKey, count, { localeCount })
    },
    audioTrackSize() {
      return this.isFilterVisible ? 'm' : 's'
    },
  },
  methods: {
    ...mapActions(MEDIA, { fetchMedia: FETCH_MEDIA }),
    onLoadMoreAudios() {
      const searchParams = {
        page: this.results.page + 1,
        shouldPersistMedia: true,
        ...this.query,
      }
      this.$emit('onLoadMoreAudios', searchParams)
    },
  },
}
</script>

<style lang="scss" scoped>
.audio-track {
  @apply pb-10;
}

.load-more {
  text-align: center;

  button {
    color: #23282d;
    margin-top: 2rem;
    border: 1px solid rgba(35, 40, 45, 0.2);
    font-size: 1.2em;

    &:hover {
      color: white;
    }
    &:disabled {
      opacity: 1;
      &:hover {
        color: black;
      }
    }

    @include mobile {
      padding: 0.5rem;

      span {
        font-size: 0.9rem;
      }
    }
  }
}

.results-meta {
  @apply px-6 pt-2;

  @screen lg {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
