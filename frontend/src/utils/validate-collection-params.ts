import { Context } from "@nuxt/types"
import { Pinia } from "pinia"

import { SupportedMediaType } from "~/constants/media"
import {
  CollectionParams,
  CreatorCollection,
  SourceCollection,
} from "~/types/search"
import { useProviderStore } from "~/stores/provider"
import { warn } from "~/utils/console"
import { useFeatureFlagStore } from "~/stores/feature-flag"

export function validateCollectionParams({
  firstParam,
  mediaType,
  params,
  $pinia,
}: {
  firstParam: "tag" | "source"
  mediaType: SupportedMediaType
  params: Context["params"]
  $pinia: Pinia
}): CollectionParams | null {
  // This page is shown only when the feature flag is `on`.
  if (!useFeatureFlagStore($pinia).isOn("additional_search_views")) {
    return null
  }
  return _validate({ firstParam, mediaType, params, $pinia })
}

function parseCollectionPath(
  pathMatch: string
): SourceCollection | CreatorCollection | null {
  // Build collection params.
  // pathMatch is the part of the path after the collection name:
  //`/sourceName` or `/sourceName/creator/creatorName`.
  const pathMatchParts = pathMatch
    .split("/")
    .map((part) => part.trim())
    .filter((part) => part !== "")

  if (pathMatchParts.length === 1) {
    return { collection: "source", source: pathMatchParts[0] }
  } else if (pathMatchParts.length === 3 && pathMatchParts[1] === "creator") {
    return {
      collection: "creator",
      creator: pathMatchParts[2],
      source: pathMatchParts[0],
    }
  }
  return null
}

export function _validate({
  firstParam,
  mediaType,
  params,
  $pinia,
}: {
  firstParam: "tag" | "source"
  mediaType: SupportedMediaType
  params: Context["params"]
  $pinia: Pinia
}): CollectionParams | null {
  if (firstParam === "tag") {
    return params.tag ? { collection: "tag", tag: params.tag } : null
  }

  const collectionParams = parseCollectionPath(params.pathMatch)
  if (!collectionParams) {
    return null
  }
  // Validate source param
  if (
    !useProviderStore($pinia).isSourceNameValid(
      mediaType,
      collectionParams.source
    )
  ) {
    warn(
      `Invalid source name "${collectionParams.source}" for a ${collectionParams.collection} collection page.`
    )
    return null
  }
  return collectionParams
}
