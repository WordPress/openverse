<template>
  <section v-if="resultsCount">
    <header
      v-if="query.q && isSupported"
      class="mt-4"
      :class="isAllView ? 'mb-10' : 'mb-8'"
    >
      <VSearchResultsTitle
        class="leading-10"
        :size="isAllView ? 'large' : 'default'"
      >
        {{ query.q }}
      </VSearchResultsTitle>
    </header>

    <slot name="media" />

    <VMetaSearchForm
      v-if="!fetchState.isFetching"
      :type="metaSearchFormType"
      :has-no-results="hasNoResults"
      :query="query"
      :is-supported="isSupported"
    />
  </section>
  <VErrorSection v-else-if="!fetchState.isFetching" class="w-full py-10">
    <template #image>
      <VErrorImage :error-code="NO_RESULT" />
    </template>
    <VNoResults :type="metaSearchFormType" :query="query" />
  </VErrorSection>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'

import { ALL_MEDIA, IMAGE, supportedSearchTypes } from '~/constants/media'
import { NO_RESULT } from '~/constants/errors'

import VMetaSearchForm from '~/components/VMetaSearch/VMetaSearchForm.vue'
import VErrorSection from '~/components/VErrorSection/VErrorSection.vue'
import VErrorImage from '~/components/VErrorSection/VErrorImage.vue'
import VNoResults from '~/components/VErrorSection/VNoResults.vue'
import VSearchResultsTitle from '~/components/VSearchResultsTitle.vue'

export default {
  name: 'VSearchGrid',
  components: {
    VErrorSection,
    VMetaSearchForm,
    VErrorImage,
    VNoResults,
    VSearchResultsTitle,
  },
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
      type: /** @type {import('@nuxtjs/composition-api').PropType<import('../store/types').SupportedSearchType>} */ (
        String
      ),
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
    const hasNoResults = computed(() => {
      // noResult is hard-coded for search types that are not currently
      // supported by Openverse built-in search
      return props.supported
        ? props.query.q !== '' && props.resultsCount === 0
        : false
    })
    const isSupported = computed(() => {
      return supportedSearchTypes.includes(props.searchType)
    })
    const metaSearchFormType = computed(() => {
      return props.searchType === ALL_MEDIA ? IMAGE : props.searchType
    })
    const isAllView = computed(() => {
      return props.searchType === ALL_MEDIA
    })

    return {
      hasNoResults,
      isSupported,
      metaSearchFormType,
      isAllView,
      NO_RESULT,
    }
  },
}
</script>
