import { createError, defineNuxtRouteMiddleware } from "#imports"

import { isShallowEqualObjects } from "@wordpress/is-shallow-equal"

import { useMediaStore } from "~/stores/media"
import { useProviderStore } from "~/stores/provider"
import { useSearchStore } from "~/stores/search"

import { queryDictionaryToQueryParams } from "~/utils/search-query-transform"
import {
  isSupportedMediaType,
  type SupportedMediaType,
} from "~/constants/media"
import type {
  CollectionParams,
  CreatorCollection,
  SourceCollection,
  TagCollection,
} from "~/types/search"

import { getRouteNameString } from "~/utils/route-utils"

import type { RouteLocationNormalized } from "vue-router"

const queryToCollectionParams = (
  query: RouteLocationNormalized["query"]
): CollectionParams | undefined => {
  query = queryDictionaryToQueryParams(query)
  if ("tag" in query) {
    return {
      collection: "tag",
      tag: query.tag,
    } as TagCollection
  }

  if ("creator" in query && "source" in query) {
    return {
      collection: "creator",
      creator: query.creator,
      source: query.source,
    } as CreatorCollection
  }

  if ("source" in query) {
    return {
      collection: "source",
      source: query.source,
    } as SourceCollection
  }
  return undefined
}

const routeNameToMediaType = (
  route: RouteLocationNormalized
): SupportedMediaType | null => {
  const firstPart = getRouteNameString(route).split("-")[0]
  return firstPart && isSupportedMediaType(firstPart) ? firstPart : null
}

/**
 * Middleware for the collection routes.
 * Checks that the feature flag is enabled and that the route (name and query) is valid.
 * Extracts the collectionParams from the route and updates the search store.
 * If the source name does not exist in the provider store, it will throw a 404 error.
 */

export const collectionMiddleware = defineNuxtRouteMiddleware(async (to) => {
  const mediaStore = useMediaStore()
  const searchStore = useSearchStore()
  // Route name has the locale in it, e.g. `audio-collection__en`
  const mediaType = routeNameToMediaType(to)
  const collectionParams = queryToCollectionParams(to.query)

  if (mediaType === null || collectionParams === undefined) {
    throw createError({
      statusCode: 404,
      message: "Invalid collection route",
    })
  }

  if ("source" in collectionParams) {
    const providerStore = useProviderStore()
    if (!providerStore.isSourceNameValid(mediaType, collectionParams.source)) {
      throw createError({
        statusCode: 404,
        message: `Invalid source name ${collectionParams.source} for media type ${mediaType}`,
      })
    }
  }

  // Update the search store with the new collection state
  // This will also clear the media items in the media store,
  // so we only call it if the collection state has changed.
  if (
    searchStore.collectionParams === null ||
    !isShallowEqualObjects(searchStore.collectionParams, collectionParams) ||
    searchStore.searchType !== mediaType
  ) {
    searchStore.setCollectionState(collectionParams, mediaType)
  }

  if (import.meta.server) {
    await mediaStore.fetchMedia()
  }
})
