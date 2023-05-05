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
        {{ searchTerm }}
      </VSearchResultsTitle>
    </header>

    <slot name="media" />

    <VExternalSearchForm
      :type="externalSourcesType"
      :has-no-results="hasNoResults"
      :external-sources="externalSources"
      :search-term="searchTerm"
      :is-supported="supported"
    />
  </section>
  <VErrorSection v-else class="w-full py-10">
    <template #image>
      <VErrorImage error-code="NO_RESULT" />
    </template>
    <VNoResults
      :external-sources="externalSources"
      :search-term="searchTerm"
      :media-type="externalSourcesType"
    />
  </VErrorSection>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import {
  ALL_MEDIA,
  IMAGE,
  SearchType,
  isSupportedMediaType,
} from "~/constants/media"
import { NO_RESULT } from "~/constants/errors"
import { defineEvent } from "~/types/emits"
import type { FetchState } from "~/types/fetch-state"
import type { ApiQueryParams } from "~/utils/search-query-transform"
import { getAdditionalSources } from "~/utils/get-additional-sources"

import VExternalSearchForm from "~/components/VExternalSearch/VExternalSearchForm.vue"
import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"
import VErrorImage from "~/components/VErrorSection/VErrorImage.vue"
import VNoResults from "~/components/VErrorSection/VNoResults.vue"
import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"

export default defineComponent({
  name: "VSearchGrid",
  components: {
    VErrorSection,
    VExternalSearchForm,
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
        ? Boolean(
            props.query.q !== "" &&
              props.fetchState.hasStarted &&
              props.resultsCount === 0
          )
        : false
    })

    /**
     * External sources search form shows the external sources for current search type, or for images if the search type is 'All Content'.
     */
    const externalSourcesType = computed(() => {
      if (isSupportedMediaType(props.searchType)) {
        return props.searchType
      }
      return IMAGE
    })

    const isAllView = computed(() => props.searchType === ALL_MEDIA)

    const externalSources = computed(() =>
      getAdditionalSources(externalSourcesType.value, props.query)
    )

    const searchTerm = computed(() => props.query.q || "")

    return {
      hasNoResults,
      externalSourcesType,
      isAllView,
      NO_RESULT,
      externalSources,
      searchTerm,
    }
  },
})
</script>
