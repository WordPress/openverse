<template>
  <section>
    <GridSkeleton
      v-if="results.length === 0 && !fetchState.isFinished"
      is-for-tab="audio"
    />
    <VAudioTrack
      v-for="audio in results"
      :key="audio.id"
      class="mb-6"
      :audio="audio"
      :size="audioTrackSize"
      layout="row"
    />
    <VLoadMore
      v-if="canLoadMore && !fetchState.isFinished"
      :is-fetching="fetchState.isFetching"
      data-testid="load-more"
      @onLoadMore="onLoadMore"
    />
  </section>
</template>

<script>
import { computed, defineComponent, useContext } from '@nuxtjs/composition-api'
import { useLoadMore } from '~/composables/use-load-more'

import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'
import VLoadMore from '~/components/VLoadMore.vue'

import { propTypes } from './search-page.types'
import { isMinScreen } from '@/composables/use-media-query'

const AudioSearch = defineComponent({
  name: 'AudioSearch',
  components: {
    VAudioTrack,
    VLoadMore,
  },
  props: propTypes,
  setup(props) {
    const results = computed(() =>
      Object.values(props.mediaResults?.audio?.items ?? [])
    )
    const { i18n } = useContext()
    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: false })
    const audioTrackSize = computed(() => {
      return !isMinScreenMd.value ? 's' : props.isFilterVisible ? 'l' : 'm'
    })

    const isError = computed(() => !!props.fetchState.fetchingError)
    const errorHeader = computed(() => {
      const type = i18n.t('browse-page.search-form.audio')
      return i18n.t('browse-page.fetching-error', { type })
    })

    const { canLoadMore, onLoadMore } = useLoadMore(props)

    return {
      results,
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
