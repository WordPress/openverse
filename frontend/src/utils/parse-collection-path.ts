import { CreatorCollection, SourceCollection } from "~/types/search"

export function parseCollectionPath(
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
