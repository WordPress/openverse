<template>
  <section>
    <VGridSkeleton
      v-if="results.length === 0 && !fetchState.isFinished"
      is-for-tab="audio"
    />
    <VAudioTrack
      v-for="audio in results"
      :key="audio.id"
      class="mb-8 md:mb-10"
      :audio="audio"
      :size="audioTrackSize"
      layout="row"
    />
    <VLoadMore />
  </section>
</template>

<script>
import {
  computed,
  defineComponent,
  useContext,
  useMeta,
} from '@nuxtjs/composition-api'

import { useLoadMore } from '~/composables/use-load-more'
import { isMinScreen } from '~/composables/use-media-query'
import { useBrowserIsMobile } from '~/composables/use-browser-detection'

import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'

import VLoadMore from '~/components/VLoadMore.vue'

import VGridSkeleton from '~/components/VSkeleton/VGridSkeleton.vue'

import { propTypes } from './search-page.types'

const AudioSearch = defineComponent({
  name: 'AudioSearch',
  components: {
    VAudioTrack,
    VGridSkeleton,
    VLoadMore,
  },
  props: propTypes,
  setup(props) {
    const { i18n } = useContext()

    useMeta({ title: `${props.searchTerm} | Openverse` })

    const results = computed(() => props.resultItems.audio)

    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })

    // On SSR, we set the size to small if the User Agent is mobile, otherwise we set the size to medium.
    const isMobile = useBrowserIsMobile()
    const audioTrackSize = computed(() => {
      return !isMinScreenMd.value || isMobile
        ? 's'
        : props.isFilterVisible
        ? 'l'
        : 'm'
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
  head: {},
})
export default AudioSearch
</script>
