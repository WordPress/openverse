<template>
  <!--eslint-disable @intlify/vue-i18n/no-raw-text -->
  <section class="audio-info">
    <h4 class="b-header mb-6">Audio information</h4>
    <div class="mb-6 audio-info__grid">
      <img :src="audio.thumbnail" alt="thumbnail" width="110" height="110" />
      <div class="audio-info__data">
        <p>{{ audio.description }}</p>
        <AudioDetailsTags
          :tags="audio.tags"
          :show-header="false"
          class="mt-6 mb-6"
        />
        <dl v-if="audio">
          <div v-if="audio.audio_set">
            <dt>{{ $t('audio-details.table.album') }}</dt>
            <dd>
              <a :href="audio.audio_set.url">{{ audio.audio_set.name }}</a>
            </dd>
          </div>
          <div v-if="audio.category">
            <dt>{{ $t('audio-details.table.category') }}</dt>
            <dd>
              <a :href="audio.audio_set.url">{{ audio.category }}</a>
            </dd>
          </div>
          <div v-if="audio.sample_rate">
            <dt>
              {{ $t('audio-details.table.sample-rate') }}
            </dt>
            <dd>
              {{ audio.sample_rate }}
            </dd>
          </div>
          <div v-if="audio.filetype">
            <dt>
              {{ $t('audio-details.table.filetype') }}
            </dt>
            <dd>
              {{ audio.filetype.toUpperCase() }}
            </dd>
          </div>
          <div>
            <dt>
              {{ $t('audio-details.table.provider') }}
            </dt>
            <dd>
              {{ providerName }}
            </dd>
          </div>
          <div v-if="audio.source">
            <dt>
              {{ $t('audio-details.table.source') }}
            </dt>
            <dd>
              {{ sourceName }}
            </dd>
          </div>
          <div v-if="audio.genres">
            <dt>
              {{ $t('audio-details.table.genre') }}
            </dt>
            <dd>
              {{ audio.genres.join(', ') }}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  </section>
</template>

<script>
import getProviderName from '~/utils/get-provider-name'

export default {
  name: 'AudioDetailsTable',
  props: ['audio'],
  computed: {
    providerName() {
      return getProviderName(
        this.$store.state.audioProviders,
        this.$props.audio.provider
      )
    },
    sourceName() {
      return getProviderName(
        this.$store.state.audioProviders,
        this.$props.audio.source
      )
    },
  },
}
</script>

<style lang="scss" scoped>
.audio-info__grid {
  display: grid;
  grid-template-columns: 110px auto;
  grid-template-rows: repeat(auto-fit, 1fr);
  grid-gap: 1.5rem;
}
dl {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  grid-gap: 1.5rem;
}
dl div {
  display: flex;
  flex-direction: column;
}

dt {
  font-weight: 400;
  display: inline-block;
}

dd {
  font-weight: bold;
}
</style>
