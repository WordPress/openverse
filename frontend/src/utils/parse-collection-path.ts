import { useProviderStore } from "~/stores/provider"
import type { CreatorCollection, SourceCollection } from "~/types/search"
import type { SupportedMediaType } from "~/constants/media"

export const removeTrailingSlash = (path: string): string => {
  return path.replace(/\/$/g, "")
}
export const encodeAndReplaceSlash = (s: string) => {
  return encodeURIComponent(s.replace(/\//g, "%2F"))
}

/**
 * Parse the path to determine the source, and creator, if present.
 *
 * @param pathMatch - the part of the path after `/source/`, does not
 * start with a slash. `pathMatch` is URL decoded, so to handle `/` in
 * creator, we also need the non-decoded `fullPath`.
 * @param creator - the full path of the route, used to extract the creator
 * without URL decoding.
 * @param mediaType - the media type of the collection
 */
export function parseCollectionPath(
  pathMatch: string,
  creator: string,
  mediaType: SupportedMediaType
): SourceCollection | CreatorCollection | null {
  const pathWithoutTrailingSlash = removeTrailingSlash(pathMatch)

  const pathParts = pathWithoutTrailingSlash.split("/", 2).filter(Boolean)

  if (
    !pathParts.length ||
    (pathParts.length === 2 && pathParts[1] !== "creator")
  ) {
    return null
  }

  const source = pathParts[0]
  const providerStore = useProviderStore()
  if (!providerStore.isSourceNameValid(mediaType, source)) {
    return null
  }

  if (pathParts.length === 1) {
    return { collection: "source", source }
  }

  if (!creator || creator.includes("/")) {
    return null
  }
  return { collection: "creator", creator: decodeURIComponent(creator), source }
}
