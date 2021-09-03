<template>
  <section>
    <div v-show="!isFetchingAudios && includeAnalytics" class="results-meta">
      <span class="caption font-semibold">
        {{ audiosCount }}
      </span>
    </div>
    <div class="px-6">
      <ClientOnly>
        <AudioTrack
          v-for="audio in audios"
          :key="audio.id"
          :audio="audio"
          :is-compact="true"
        />
      </ClientOnly>
    </div>
  </section>
</template>

<script>
// import { AUDIO } from '~/constants/media'

export default {
  name: 'AudioResultsList',
  props: {
    includeAnalytics: {
      default: true,
    },
  },
  computed: {
    audios() {
      return this.$store.state.audios
    },
    audiosCount() {
      const count = this.$store.state.count.audios
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
    isFetchingAudiosError() {
      return this.$store.state.isFetchingError.audios
    },
    isFetchingAudios() {
      return this.$store.state.isFetching.audios
    },
  },
}
</script>

<style lang="scss" scoped>
.audio-track {
  @apply pb-10;
}
.results-meta {
  @apply px-6 py-2;

  @include desktop {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
