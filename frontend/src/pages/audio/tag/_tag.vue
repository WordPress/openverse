<template>
  <VCollectionPage
    v-if="collectionParams"
    :collection-params="collectionParams"
    :results="results"
    media-type="audio"
  />
</template>

<script lang="ts">
import { computed, ref } from "vue"
import { defineComponent, useFetch } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"
import { AUDIO } from "~/constants/media"
import { useMediaStore } from "~/stores/media"
import { validateCollectionParams } from "~/utils/validate-collection-params"

import { Results } from "~/types/result"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineComponent({
  name: "VAudioTagPage",
  components: { VCollectionPage },
  layout: "content-layout",
  /**
   * Validate the dynamic path parameters and update the search store.
   * Shows an error page if `validate` returns `false`.
   */
  validate({ params, $pinia }): boolean {
    const mediaType = AUDIO
    const collectionParams = validateCollectionParams({
      firstParam: "tag",
      mediaType,
      params,
      $pinia,
    })
    if (!collectionParams) return false
    useSearchStore($pinia).setCollectionState(collectionParams, mediaType)
    return true
  },
  setup() {
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const collectionParams = computed(() => searchStore.collectionParams)

    const results = ref<Results>({ type: AUDIO, items: [] })

    useFetch(async () => {
      await mediaStore.fetchMedia()
      results.value.items = mediaStore.resultItems[AUDIO]
    })

    return {
      collectionParams,

      results,
    }
  },
})
</script>
