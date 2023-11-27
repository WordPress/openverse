<template>
  <VCollectionPage media-type="image" />
</template>

<script lang="ts">
import { defineComponent, useFetch } from "@nuxtjs/composition-api"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { validateCollectionParams } from "~/utils/validate-collection-params"
import { IMAGE } from "~/constants/media"

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

    useFetch(async () => {
      await mediaStore.fetchMedia()
    })
  },
})
</script>
