import type { CreatorCollection, SourceCollection } from "~/types/search"

const removeSlashes = (path: string): string => {
  return path.replace(/^\/|\/$/g, "")
}

export function parseCollectionPath(
  pathMatch: string
): SourceCollection | CreatorCollection | null {
  pathMatch = removeSlashes(pathMatch)
  // Build collection params.
  // pathMatch is the part of the path after the collection name:
  //`/sourceName` or `/sourceName/creator/creatorName`.
  // The creatorName can contain `/`, so we only split by slash twice.
  const pathMatchParts = pathMatch
    .split("/", 2)
    .map((part) => part.trim())
    .filter((part) => part !== "")

  if (pathMatchParts.length === 1) {
    return { collection: "source", source: pathMatchParts[0] }
  } else if (pathMatchParts[1] === "creator") {
    const rawCreator = pathMatch.split(`${pathMatchParts[0]}/creator/`)
    if (rawCreator.length === 2) {
      return {
        collection: "creator",
        creator: removeSlashes(rawCreator[1]),
        source: pathMatchParts[0],
      }
    }
  }
  return null
}
