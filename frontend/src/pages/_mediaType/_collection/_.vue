<template>
  <div class="px-6 lg:px-10"></div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api"

import { useProviderStore } from "~/stores/provider"
import { useSearchStore } from "~/stores/search"
import { isSupportedMediaType, SupportedMediaType } from "~/constants/media"
import type { Collection, CollectionParams } from "~/types/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { warn } from "~/utils/console"

export default defineComponent({
  name: "VCollectionPage",
  layout: "content-layout",
  /**
   * Validate the dynamic path parameters.
   *
   * Shows an error page if `validate` returns `false`.
   *
   * @param params - the path parameters: `mediaType`, `collection` and `pathMatch` for the rest.
   * @param $pinia - passed to update the store with the validated data.
   */
  validate({ params, $pinia }): Promise<boolean> | boolean {
    // This page is shown only when the feature flag is `on`.
    if (!useFeatureFlagStore($pinia).isOn("additional_search_views")) {
      return false
    }
    // Validate media type
    if (!isSupportedMediaType(params.mediaType)) {
      return false
    }
    const mediaType = params.mediaType as SupportedMediaType

    // Validate collection
    // `source` is the second path parameter for both source and creator views.
    if (!["tag", "source"].includes(params.collection)) {
      return false
    }

    // Build collection params.
    // pathMatch is the part of the path after the collection name:
    // `/tagName` or `/sourceName` or `/sourceName/creator/creatorName`.
    const pathMatchParts = params.pathMatch
      .split("/")
      .map((part) => part.trim())
      .filter((part) => part !== "")

    // The path parts must be either ["tagName"], ["sourceName"] or  ["sourceName", "creator", "creatorName"].
    let collection: Collection
    let collectionParams: CollectionParams
    if (pathMatchParts.length === 1 && params.collection === "source") {
      collection = "source"
      collectionParams = { collection, source: pathMatchParts[0] }
    } else if (pathMatchParts.length === 1 && params.collection === "tag") {
      collection = "tag"
      collectionParams = { collection, tag: pathMatchParts[0] }
    } else if (pathMatchParts.length === 3 && params.collection === "source") {
      collection = "creator"
      const [source, , creator] = pathMatchParts
      collectionParams = { collection, creator, source }
    } else {
      return false
    }

    // Validate source param
    if (collectionParams.collection !== "tag") {
      if (
        !useProviderStore($pinia).isSourceNameValid(
          mediaType,
          collectionParams.source
        )
      ) {
        warn(
          `Attempting to get a ${collectionParams.collection} collection for an invalid source name: ${collectionParams.source}`
        )
        return false
      }
    }

    // Update the search store
    const searchStore = useSearchStore($pinia)
    searchStore.setStrategy(collection, collectionParams)
    searchStore.setSearchType(mediaType)
    return true
  },
})
</script>
