<template>
  <section>
    <div v-show="!isFetchingAudios && includeAnalytics" class="results-meta">
      <span class="caption font-semibold">
        {{ audiosCount }}
      </span>
    </div>
    <div class="px-6 pt-6">
      <AudioTrack
        v-for="audio in audios"
        :key="audio.id"
        :audio="audio"
        :size="audioTrackSize"
        layout="row"
      />
    </div>
    <div v-if="!isFetchingAudiosError" class="load-more">
      <button
        v-show="!isFetchingAudios && includeAnalytics"
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
      <LoadingIcon v-show="isFetchingAudios" />
    </div>
    <div v-if="isFetchingAudiosError" class="m-auto w-1/2 text-center pt-6">
      <h5>
        {{
          $t('browse-page.fetching-error', {
            type: $t('browse-page.search-form.audio'),
          })
        }}
        {{ errorMessage }}
      </h5>
    </div>
  </section>
</template>

<script>
import { FETCH_MEDIA } from '~/constants/action-types'
import { AUDIO } from '~/constants/media'
import { mapActions, mapState } from 'vuex'

export default {
  name: 'AudioResultsList',
  props: {
    query: {},
    includeAnalytics: {
      default: true,
    },
  },
  async fetch() {
    if (!this.audios.length) {
      await this.fetchMedia({
        ...this.$store.state.query,
        mediaType: AUDIO,
      })
    }
  },
  computed: {
    ...mapState(['audios', 'errorMessage', 'isFilterVisible']),
    ...mapState({
      isFetchingAudios: 'isFetching.audios',
      isFetchingAudiosError: 'isFetchingError.audios',
      resultsCount: 'audiosCount',
      currentPage: 'audioPage',
      audioPageCount: 'pageCount.audios',
    }),
    audiosCount() {
      const count = this.resultsCount
      if (count === 0) {
        return this.$t('browse-page.audio-no-results')
      }
      return count >= 10000
        ? this.$tc('browse-page.audio-result-count-more', count, {
            localeCount: count.toLocaleString(this.$i18n.locale),
          })
        : this.$tc('browse-page.audio-result-count', count, {
            localeCount: count.toLocaleString(this.$i18n.locale),
          })
    },
    isFinished() {
      return this.currentPage >= this.audioPageCount
    },
    audioTrackSize() {
      return this.isFilterVisible ? 'm' : 's'
    },
  },
  methods: {
    ...mapActions({
      fetchMedia: FETCH_MEDIA,
    }),
    onLoadMoreAudios() {
      const searchParams = {
        page: this.currentPage + 1,
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

  @include desktop {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
