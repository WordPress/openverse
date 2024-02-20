import { isClient } from "@vueuse/core"

import { useFeatureFlagStore } from "~/stores/feature-flag"

import { AUDIO, IMAGE } from "~/constants/media"
import { useSearchStore } from "~/stores/search"
import { parseCollectionPath } from "~/utils/parse-collection-path"

import type { Middleware } from "@nuxt/types"

export const collectionMiddleware: Middleware = async ({
  $pinia,
  error: nuxtError,
  route,
}) => {
  if (!useFeatureFlagStore($pinia).isOn("additional_search_views")) {
    nuxtError({
      statusCode: 404,
      message: "Additional search views are not enabled",
    })
  }

  const mediaType = route.fullPath.includes("/image/")
    ? IMAGE
    : route.fullPath.includes("/audio/")
    ? AUDIO
    : null
  // This should never happen, but adding it for type safety.
  if (!mediaType) {
    throw new Error("Invalid media type")
  }

  const searchStore = useSearchStore($pinia)

  if (route.fullPath.includes(`${mediaType}/tag/`)) {
    const tag = route.params.tag
    if (!tag) {
      nuxtError({
        statusCode: 404,
        message: "Invalid tag path",
      })
    }
    searchStore.setCollectionState({ tag, collection: "tag" }, mediaType)
    return
  }

  let creator = ""
  if (route.fullPath.includes("/creator/")) {
    creator = route.fullPath.split("/creator/")[1]
    if (isClient) {
      // On the client, the slashes in the creator part of the path are decoded.
      // We encode them back to correctly parse the path below.
      creator = creator.replace(/\/$/g, "").replace("/", "%2F")
    }
  }
  const collectionParams = parseCollectionPath(
    route.params.pathMatch,
    creator,
    mediaType
  )

  if (collectionParams) {
    searchStore.setCollectionState(collectionParams, mediaType)
    return
  }

  nuxtError({
    statusCode: 404,
    message: "Invalid collection path",
  })
}
