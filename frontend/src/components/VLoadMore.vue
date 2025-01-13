<script setup lang="ts">
import { useI18n, useNuxtApp, useRoute } from "#imports"
import { computed, onMounted, ref, watch } from "vue"

import { storeToRefs } from "pinia"
import { useElementVisibility } from "@vueuse/core"

import type { SupportedSearchType } from "#shared/constants/media"
import type { SingleResultProps } from "#shared/types/collection-component-props"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"

import VButton from "~/components/VButton.vue"

defineProps<
  SingleResultProps & {
    searchType: SupportedSearchType
    canLoadMore: boolean
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
  return {
    ...searchStore.searchParamsForEvent,
    resultPage: currentPage.value || 1,
  }
})

const isFetching = computed(() => mediaStore.isFetching)

const reachResultEndEventSent = ref(false)
/**
 * On button click, send the analytics events and emit `load-more` event.
 *
 * The button is disabled when we are fetching, but we still check
 * whether we are currently fetching to be sure we don't fetch multiple times.
 *
 */
const onLoadMore = async () => {
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
  isFetching.value ? t("browsePage.loading") : t("browsePage.load")
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
