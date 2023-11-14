<template>
  <VCollectionPage
    v-if="collectionParams"
    :collection-params="collectionParams"
    :results="results"
    media-type="image"
  />
</template>

<script lang="ts">
import { computed, ref } from "vue"
import { defineComponent, useFetch } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"
import { IMAGE } from "~/constants/media"
import { validateCollectionParams } from "~/utils/validate-collection-params"

import type { Results } from "~/types/result"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineComponent({
  name: "VImageTagPage",
  components: { VCollectionPage },
  layout: "content-layout",
  /**
   * Validate the dynamic path parameters.
   *
   * Shows an error page if `validate` returns `false`.
   *
   * @param params - the path parameters: `mediaType`, `collection` and `pathMatch` for the rest.
   * @param $pinia - passed to update the store with the validated data.
   */
  validate({ params, $pinia }): boolean {
    const mediaType = IMAGE
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

    const results = ref<Results>({ type: IMAGE, items: [] })

    useFetch(async () => {
      await mediaStore.fetchMedia()
      results.value.items = mediaStore.resultItems[IMAGE]
    })

    return {
      collectionParams,

      results,
    }
  },
})
</script>
