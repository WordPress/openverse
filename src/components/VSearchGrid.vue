<template>
  <section class="search-grid">
    <VSearchResultsTitle
      v-if="query.q && isSupported"
      class="leading-10"
      :size="isAllView ? 'large' : 'default'"
    >
      {{ query.q }}
    </VSearchResultsTitle>
    <div
      v-if="shouldShowMeta"
      class="results-meta flex flex-col sm:flex-row items-start justify-between px-6"
      data-testid="search-meta"
    >
      <div
        class="font-semibold caption leading-10 flex flex-col sm:flex-row sm:me-auto justify-between"
      >
        <span class="pe-6">
          {{ mediaCount }}
        </span>
        <VSearchRating
          v-if="query.q"
          :search-term="query.q"
          class="leading-10"
        />
      </div>
      <VSaferBrowsing />
    </div>
    <slot name="media" />

    <VMetaSearchForm
      v-if="!fetchState.isFetching"
      :type="metaSearchFormType"
      :noresult="noresult"
      :query="query"
      :supported="isSupported"
    />
  </section>
</template>

<script>
import { computed, useContext } from '@nuxtjs/composition-api'
import { AUDIO, IMAGE } from '~/constants/media'

import VSaferBrowsing from '~/components/VSaferBrowsing.vue'
import VSearchRating from '~/components/VSearchRating.vue'
import VMetaSearchForm from '~/components/VMetaSearch/VMetaSearchForm.vue'

const i18nKeys = {
  [AUDIO]: {
    noResult: 'browse-page.audio-no-results',
    result: 'browse-page.audio-result-count',
    more: 'browse-page.audio-result-count-more',
  },
  [IMAGE]: {
    noResult: 'browse-page.image-no-results',
    result: 'browse-page.image-result-count',
    more: 'browse-page.image-result-count-more',
  },
}

export default {
  name: 'VSearchGrid',
  components: { VMetaSearchForm, VSaferBrowsing, VSearchRating },
  props: {
    supported: {
      type: Boolean,
      required: true,
    },
    query: {
      type: Object,
      required: true,
    },
    searchType: {
      type: String,
      required: true,
    },
    fetchState: {
      required: true,
    },
    resultsCount: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const { i18n } = useContext()
    const shouldShowMeta = computed(() => {
      return (
        props.supported &&
        props.query.q.trim() !== '' &&
        !props.fetchState.isFetching
      )
    })
    /**
     * The translated string showing how many results were found for
     * this media type.
     *
     * @returns {string}
     */
    const mediaCount = computed(() => {
      if (!props.supported) return

      const count = props.resultsCount
      const countKey =
        count === 0 ? 'noResult' : count >= 10000 ? 'more' : 'result'
      const i18nKey = i18nKeys[props.query.mediaType][countKey]
      const localeCount = count.toLocaleString(i18n.locale)
      return i18n.tc(i18nKey, count, { localeCount })
    })

    const noresult = computed(() => {
      // noresult is hard-coded for search types that are not currently
      // supported by Openverse built-in search
      return props.supported
        ? props.query.q !== '' && props.resultsCount === 0
        : false
    })
    const isSupported = computed(() => {
      return props.searchType === 'all' ? true : props.supported
    })
    const metaSearchFormType = computed(() => {
      return props.searchType === 'all' ? 'image' : props.searchType
    })
    const isAllView = computed(() => {
      return props.searchType === 'all'
    })

    return {
      mediaCount,
      noresult,
      shouldShowMeta,
      isSupported,
      metaSearchFormType,
      isAllView,
    }
  },
}
</script>
