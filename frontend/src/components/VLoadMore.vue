<template>
  <div ref="loadMoreSectionRef" class="w-full">
    <VButton
      v-show="canLoadMore"
      class="label-bold lg:description-bold h-16 w-full lg:h-18"
      variant="filled-gray"
      size="disabled"
      :disabled="isFetching"
      data-testid="load-more"
      @click="onLoadMore"
    >
      {{ buttonLabel }}
    </VButton>
  </div>
</template>
<script lang="ts">
import {
  computed,
  defineComponent,
  onMounted,
  type PropType,
  ref,
  watch,
} from "vue"
import { storeToRefs } from "pinia"
import { useElementVisibility } from "@vueuse/core"

import { useContext, useRoute } from "@nuxtjs/composition-api"

import { useMediaStore } from "~/stores/media"
import { useI18n } from "~/composables/use-i18n"
import { defineEvent } from "~/types/emits"

import type { ResultKind } from "~/types/result"
import type { SupportedSearchType } from "~/constants/media"

import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VLoadMore",
  components: {
    VButton,
  },
  props: {
    searchType: {
      type: String as PropType<SupportedSearchType>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
    kind: {
      type: String as PropType<ResultKind>,
      required: true,
    },
    isFetching: {
      type: Boolean,
      required: true,
    },
  },
  emits: {
    "load-more": defineEvent(),
  },
  setup(props, { emit }) {
    const loadMoreSectionRef = ref(null)
    const route = useRoute()
    const i18n = useI18n()
    const mediaStore = useMediaStore()
    const { $sendCustomEvent } = useContext()

    const { currentPage } = storeToRefs(mediaStore)

    const eventPayload = computed(() => {
      return {
        searchType: props.searchType,
        query: props.searchTerm,
        resultPage: currentPage.value || 1,
      }
    })

    /**
     * Whether we should show the "Load more" button.
     * If the fetching for the current query has started, there is at least
     * 1 page of results, there has been no fetching error, and there are
     * more results to fetch, we show the button.
     */
    const canLoadMore = computed(() => mediaStore.canLoadMore)

    const reachResultEndEventSent = ref(false)
    /**
     * On button click, send the analytics events and emit `load-more` event.
     *
     * The button is disabled when we are fetching, but we still check
     * whether we are currently fetching to be sure we don't fetch multiple times.
     *
     */
    const onLoadMore = async () => {
      if (props.isFetching) {
        return
      }

      reachResultEndEventSent.value = false

      $sendCustomEvent("LOAD_MORE_RESULTS", eventPayload.value)

      emit("load-more")
    }

    const sendReachResultEnd = () => {
      // This function can be called before the media is fetched and
      // currentPage is updated from 0, so we use the value or 1.
      // The currentPage can never be 0 here because then the loadMore
      // button would not be visible.
      $sendCustomEvent("REACH_RESULT_END", eventPayload.value)
    }

    const buttonLabel = computed(() =>
      props.isFetching
        ? i18n.t("browsePage.loading")
        : i18n.t("browsePage.load")
    )
    const mainPageElement = ref<HTMLElement | null>(null)
    onMounted(() => {
      mainPageElement.value = document.getElementById("main-page")
    })
    const isLoadMoreButtonVisible = useElementVisibility(loadMoreSectionRef, {
      scrollTarget: mainPageElement,
    })

    // Reset the reachResultEndEvent whenever the route changes,
    // to make sure the result end is tracked properly whenever
    // the search query or content type changes
    watch(route, () => {
      reachResultEndEventSent.value = false
    })

    watch(isLoadMoreButtonVisible, (isVisible) => {
      if (isVisible) {
        if (reachResultEndEventSent.value) {
          return
        }
        sendReachResultEnd()
        reachResultEndEventSent.value = true
      }
    })

    return {
      buttonLabel,
      onLoadMore,
      canLoadMore,

      loadMoreSectionRef,
    }
  },
})
</script>
