<template>
  <section>
    <div v-show="!isFetching" class="results-meta">
      <span class="caption font-semibold">
        {{ _audiosCount }}
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
    <div v-if="!isFetchingError" class="load-more">
      <button
        v-show="!isFetching"
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
      <LoadingIcon v-show="isFetching" />
    </div>
    <div v-if="isFetchingError" class="m-auto w-1/2 text-center pt-6">
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
import { mapActions, mapGetters, mapState } from 'vuex'
import { FETCH_MEDIA } from '~/constants/action-types'
import { AUDIO } from '~/constants/media'
import { FILTER, SEARCH } from '~/constants/store-modules'

export default {
  name: 'AudioResultsList',
  async fetch() {
    if (!this.audios.length) {
      await this.fetchMedia({
        ...this.query,
        mediaType: AUDIO,
      })
    }
  },
  computed: {
    ...mapState(SEARCH, [
      'audios',
      'errorMessage',
      'audiosCount',
      'audioPage',
      'pageCount',
      'query',
    ]),
    ...mapGetters(SEARCH, ['isFetching', 'isFetchingError']),
    ...mapState(FILTER, ['isFilterVisible']),
    _audiosCount() {
      const count = this.audiosCount
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
      return this.audioPage >= this.pageCount.audio
    },
    audioTrackSize() {
      return this.isFilterVisible ? 'm' : 's'
    },
  },
  methods: {
    ...mapActions(SEARCH, { fetchMedia: FETCH_MEDIA }),
    onLoadMoreAudios() {
      const searchParams = {
        page: this.audioPage + 1,
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
