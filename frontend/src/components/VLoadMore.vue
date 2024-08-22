<script setup lang="ts">
import { useI18n, useNuxtApp, useRoute } from "#imports"

import { computed, onMounted, ref, watch } from "vue"
import { storeToRefs } from "pinia"
import { useElementVisibility } from "@vueuse/core"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"

import type { ResultKind } from "~/types/result"
import type { Collection } from "~/types/search"
import type { SingleResultProps } from "~/types/collection-component-props"
import type { SupportedSearchType } from "~/constants/media"

import VButton from "~/components/VButton.vue"

const props = defineProps<
  SingleResultProps & {
    searchType: SupportedSearchType
    isFetching: boolean
  }
>()

const emit = defineEmits<{
  "load-more": []
}>()

const loadMoreSectionRef = ref(null)
const route = useRoute()
const { t } = useI18n({ useScope: "global" })
const mediaStore = useMediaStore()
const searchStore = useSearchStore()
const { $sendCustomEvent } = useNuxtApp()

const { currentPage } = storeToRefs(mediaStore)

const eventPayload = computed(() => {
  let kind: ResultKind =
    searchStore.strategy === "default" ? "search" : "collection"
  const collectionType = (searchStore.collectionValue as Collection) ?? "null"
  return {
    searchType: props.searchType,
    query: props.searchTerm,
    resultPage: currentPage.value || 1,
    kind,
    collectionType,
    collectionValue: searchStore.collectionValue ?? "null",
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
  props.isFetching ? t("browsePage.loading") : t("browsePage.load")
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
</script>

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
