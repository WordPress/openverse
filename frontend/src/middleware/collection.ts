import {
  defineNuxtRouteMiddleware,
  firstParam,
  navigateTo,
  parseCollectionPath,
} from "#imports"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useMediaStore } from "~/stores/media"
import { useProviderStore } from "~/stores/provider"
import { useSearchStore } from "~/stores/search"

import type { SupportedMediaType } from "~/constants/media"
import type { CollectionParams } from "~/types/search"

const extractMediaType = (path: string): SupportedMediaType => {
  if (path.includes("/image/")) {
    return "image"
  } else if (path.includes("/audio/")) {
    return "audio"
  } else {
    throw new Error(`Unknown media type for path ${path}`)
  }
}
export const collectionMiddleware = defineNuxtRouteMiddleware(async (to) => {
  if (!useFeatureFlagStore().isOn("additional_search_views")) {
    return navigateTo("/")
  }

  const mediaType = extractMediaType(to.path)
  if (!mediaType) {
    throw createError({
      statusCode: 404,
      message: `Unknown media type in path ${to.path}`,
    })
  }

  let collectionParams: CollectionParams | null = null
  if (to.params.tag) {
    const tag = firstParam(to.params.tag)
    if (!tag) {
      throw createError({
        statusCode: 404,
        message: `Invalid tag path: ${to.path}`,
      })
    }
    collectionParams = { collection: "tag", tag }
  } else if (to.params.source) {
    const rawCollectionParams = parseCollectionPath(to.params.source)
    const providerStore = useProviderStore()
    await providerStore.fetchMediaTypeProviders(mediaType)
    if (
      rawCollectionParams &&
      useProviderStore().isSourceNameValid(
        mediaType,
        rawCollectionParams.source
      )
    ) {
      collectionParams = rawCollectionParams
    }
  }
  if (!collectionParams) {
    throw createError({
      statusCode: 404,
      message: `Invalid collection path: ${to.path}`,
    })
  }
  const searchStore = useSearchStore()
  searchStore.setCollectionState(collectionParams, mediaType)

  if (process.server) {
    const mediaStore = useMediaStore()
    await mediaStore.fetchMedia()
  }
})
