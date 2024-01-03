import type { CreatorCollection, SourceCollection } from "~/types/search"

import type { LocationQueryValue } from "vue-router"

export function parseCollectionPath(
  sourceParams: LocationQueryValue | LocationQueryValue[]
): SourceCollection | CreatorCollection | null {
  if (!sourceParams) {
    return null
  }
  const pathMatchParts =
    typeof sourceParams === "string"
      ? [sourceParams]
      : (sourceParams.filter((part) => Boolean(part)) as string[])

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
