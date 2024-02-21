import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { parseCollectionPath } from "~/utils/parse-collection-path"
import { useProviderStore } from "~/stores/provider"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { IMAGE } from "~/constants/media"

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
    const collection = parseCollectionPath(
      "flickr",
      "/image/source/flickr/",
      IMAGE
    )

    expect(collection).toEqual({ source: "flickr", collection: "source" })
  })
  it("returns source collection from a localized path", () => {
    const collection = parseCollectionPath(
      "flickr",
      "/en-za/image/source/flickr/",
      IMAGE
    )

    expect(collection).toEqual({ source: "flickr", collection: "source" })
  })

  it("returns null if `creator` parameter is blank", () => {
    const collection = parseCollectionPath(
      "flickr/creator/",
      "/image/source/flickr/creator/",
      IMAGE
    )

    expect(collection).toBeNull()
  })
  it("returns creator collection without trailing slash", () => {
    const collection = parseCollectionPath("flickr/creator/me", "me", IMAGE)

    expect(collection).toEqual({
      source: "flickr",
      creator: "me",
      collection: "creator",
    })
  })

  it("returns creator collection with trailing slash", () => {
    const collection = parseCollectionPath("flickr/creator/me/", "me", IMAGE)

    expect(collection).toEqual({
      source: "flickr",
      creator: "me",
      collection: "creator",
    })
  })

  it("returns null if creator name contains non-encoded slashes", () => {
    const collection = parseCollectionPath(
      "flickr/creator/me/you-and-them/",
      "/image/source/flickr/creator/me/you-and-them/",
      IMAGE
    )

    expect(collection).toBeNull()
  })

  it("handles encoded slashes in creator name", () => {
    const collection = parseCollectionPath(
      "flickr/creator/me%2Fyou-and-them/",
      "me%2Fyou-and-them",
      IMAGE
    )

    expect(collection).toEqual({
      source: "flickr",
      creator: "me/you-and-them",
      collection: "creator",
    })
  })

  it("handles creator names starting with encoded slashes", () => {
    const collection = parseCollectionPath(
      "flickr/creator/%2Fme%2Fyou-and-them/",
      "%2Fme%2Fyou-and-them",
      IMAGE
    )

    expect(collection).toEqual({
      source: "flickr",
      creator: "/me/you-and-them",
      collection: "creator",
    })
  })
})
