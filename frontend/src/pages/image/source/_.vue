<template>
  <VCollectionPage
    v-if="collectionParams"
    :collection-params="collectionParams"
    :results="results"
    :creator-url="creatorUrl"
    media-type="image"
  />
</template>

<script lang="ts">
import { computed, ref } from "vue"
import { defineComponent, useFetch } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"
import { IMAGE } from "~/constants/media"
import { useMediaStore } from "~/stores/media"

import { validateCollectionParams } from "~/utils/validate-collection-params"

import { Results } from "~/types/result"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineComponent({
  name: "VImageSourcePage",
  components: { VCollectionPage },
  layout: "content-layout",
  /**
   * Validate the dynamic path parameters and update the search store.
   * Shows an error page if `validate` returns `false`.
   */
  validate({ params, $pinia }): boolean {
    const mediaType = IMAGE
    const collectionParams = validateCollectionParams({
      firstParam: "source",
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

    const results = ref<Results>({ type: IMAGE, items: [] })
    const creatorUrl = ref<string | undefined>(undefined)

    useFetch(async () => {
      await mediaStore.fetchMedia()
      results.value.items = mediaStore.resultItems[IMAGE]
      if (
        collectionParams.value?.collection === "creator" &&
        results.value.items.length > 0
      ) {
        creatorUrl.value = results.value.items[0].creator_url
      }
    })

    return {
      collectionParams,

      results,
      creatorUrl,
    }
  },
})
</script>
