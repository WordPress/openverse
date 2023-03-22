<template>
  <VButton
    v-show="canLoadMore"
    size="large"
    variant="full"
    :disabled="isFetching"
    data-testid="load-more"
    @click="onLoadMore"
  >
    {{ buttonLabel }}
  </VButton>
</template>
<script lang="ts">
import { computed, defineComponent } from "vue"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useI18n } from "~/composables/use-i18n"

import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VLoadMore",
  components: {
    VButton,
  },
  setup() {
    const i18n = useI18n()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    /**
     * Whether we should show the "Load more" button.
     * If the user has entered a search term, there is at least 1 page of results,
     * there has been no fetching error, and there are more results to fetch,
     * we show the button.
     */
    const canLoadMore = computed(
      () =>
        searchStore.searchTerm !== "" &&
        !mediaStore.fetchState.fetchingError &&
        !mediaStore.fetchState.isFinished &&
        mediaStore.resultCount > 0
    )

    /**
     * On button click, fetch media, persisting the existing results.
     * The button is disabled when we are fetching, but we still check
     * whether we are currently fetching to be sure we don't fetch multiple times.
     *
     */
    const onLoadMore = async () => {
      if (isFetching.value) return

      await mediaStore.fetchMedia({
        shouldPersistMedia: true,
      })
    }

    const buttonLabel = computed(() =>
      isFetching.value
        ? i18n.t("browse-page.loading")
        : i18n.t("browse-page.load")
    )

    return {
      buttonLabel,
      isFetching,
      onLoadMore,
      canLoadMore,
    }
  },
})
</script>
