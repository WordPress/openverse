<template>
  <section
    v-if="
      !fetchState.hasStarted ||
      fetchState.isFetching ||
      (!fetchState.isFetching && resultsCount)
    "
  >
    <header
      v-if="query.q && supported"
      class="mt-5"
      :class="isAllView ? 'mb-10' : 'mb-8'"
    >
      <VSearchResultsTitle :size="isAllView ? 'large' : 'default'">
        {{ query.q }}
      </VSearchResultsTitle>
    </header>

    <slot name="media" />

    <VMetaSearchForm
      v-if="!fetchState.isFetching"
      :type="metaSearchFormType"
      :has-no-results="hasNoResults"
      :query="query"
      :is-supported="supported"
      @tab="$emit('tab', $event)"
    />
  </section>
  <VErrorSection v-else class="w-full py-10">
    <template #image>
      <VErrorImage :error-code="NO_RESULT" />
    </template>
    <VNoResults :type="metaSearchFormType" :query="query" />
  </VErrorSection>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { ALL_MEDIA, IMAGE, SearchType, mediaTypes } from '~/constants/media'
import { NO_RESULT } from '~/constants/errors'
import { defineEvent } from '~/types/emits'
import type { ApiQueryParams } from '~/utils/search-query-transform'
import type { FetchState } from '~/composables/use-fetch-state'

import VMetaSearchForm from '~/components/VMetaSearch/VMetaSearchForm.vue'
import VErrorSection from '~/components/VErrorSection/VErrorSection.vue'
import VErrorImage from '~/components/VErrorSection/VErrorImage.vue'
import VNoResults from '~/components/VErrorSection/VNoResults.vue'
import VSearchResultsTitle from '~/components/VSearchResultsTitle.vue'

export default defineComponent({
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
      type: Object as PropType<ApiQueryParams>,
      required: true,
    },
    searchType: {
      type: String as PropType<SearchType>,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState>,
      required: true,
    },
    resultsCount: {
      type: Number,
      required: true,
    },
  },
  emits: {
    tab: defineEvent<[KeyboardEvent]>(),
  },
  setup(props) {
    const hasNoResults = computed(() => {
      // noResult is hard-coded for search types that are not currently
      // supported by Openverse built-in search
      return props.supported
        ? props.query.q !== '' && props.resultsCount === 0
        : false
    })

    /**
     * Metasearch form shows the external sources for current search type, or for images if the search type is 'All Content'.
     */
    const metaSearchFormType = computed(() => {
      if (mediaTypes.includes(props.searchType)) {
        return props.searchType
      }
      return IMAGE
    })

    const isAllView = computed(() => {
      return props.searchType === ALL_MEDIA
    })

    return {
      hasNoResults,
      metaSearchFormType,
      isAllView,
      NO_RESULT,
    }
  },
})
</script>
