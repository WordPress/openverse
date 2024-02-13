import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { parseCollectionPath } from "~/utils/parse-collection-path"
import { useProviderStore } from "~/stores/provider"
import { useFeatureFlagStore } from "~/stores/feature-flag"

describe("validateCollectionParams", () => {
  /** @type { import("pinia").Pinia } **/
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    useProviderStore().isSourceNameValid = jest.fn(() => true)
    useFeatureFlagStore().toggleFeature("additional_search_views", "on")
  })

  it("returns source collection", () => {
    const collection = parseCollectionPath("/flickr")

    expect(collection).toEqual({ source: "flickr", collection: "source" })
  })

  it("returns null if `creator` parameter is blank", () => {
    const collection = parseCollectionPath("/flickr/creator/")

    expect(collection).toBeNull()
  })
  it("returns creator collection without trailing slash", () => {
    const collection = parseCollectionPath("/flickr/creator/me")

    expect(collection).toEqual({
      source: "flickr",
      creator: "me",
      collection: "creator",
    })
  })

  it("returns creator collection with trailing slash", () => {
    const collection = parseCollectionPath("/flickr/creator/me/")

    expect(collection).toEqual({
      source: "flickr",
      creator: "me",
      collection: "creator",
    })
  })

  it("handles slashes in creator name", () => {
    const collection = parseCollectionPath("/flickr/creator/me/you-and-them/")

    expect(collection).toEqual({
      source: "flickr",
      creator: "me/you-and-them",
      collection: "creator",
    })
  })
})
