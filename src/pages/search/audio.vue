<template>
  <section>
    <template v-if="supported">
      <VAudioTrack
        v-for="audio in mediaResults.items"
        :key="audio.id"
        class="px-6 mb-6"
        :audio="audio"
        :size="audioTrackSize"
        layout="row"
      />

      <template v-if="isError" class="m-auto w-1/2 text-center pt-6">
        <h5>{{ errorHeader }}</h5>
        <p>{{ fetchState.fetchingError }}</p>
      </template>
      <LoadMoreButton
        v-if="canLoadMore"
        :is-error="isError"
        :is-fetching="fetchState.isFetching"
        :is-finished="fetchState.isFinished"
        media-type="audio"
        data-testid="load-more"
        @onLoadMore="onLoadMore"
      />
    </template>
  </section>
</template>

<script>
import { computed, defineComponent, useContext } from '@nuxtjs/composition-api'
import { useLoadMore } from '~/composables/use-load-more'

import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'
import LoadMoreButton from '~/components/ImageGrid/LoadMoreButton.vue'

import { propTypes } from './search-page.types'

const AudioSearch = defineComponent({
  name: 'AudioSearch',
  components: {
    VAudioTrack,
    LoadMoreButton,
  },
  props: propTypes,
  setup(props) {
    const { i18n } = useContext()

    const audioTrackSize = computed(() => (props.isFilterVisible ? 'm' : 's'))

    const isError = computed(() => !!props.fetchState.fetchingError)
    const errorHeader = computed(() => {
      const type = i18n.t('browse-page.search-form.audio')
      return i18n.t('browse-page.fetching-error', { type })
    })

    const { canLoadMore, onLoadMore } = useLoadMore(props)

    return {
      audioTrackSize,
      isError,
      errorHeader,

      canLoadMore,
      onLoadMore,
    }
  },
})
export default AudioSearch
</script>
