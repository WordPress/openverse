import { h } from "vue"

import { useMediaStore } from "~/stores/media"
import { useProviderStore } from "~/stores/provider"

import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"

import type { StoryObj } from "@storybook/vue3"

const imageProviders = [
  {
    source_name: "smithsonian_african_american_history_museum",
    display_name:
      "Smithsonian Institution: National Museum of African American History and Culture",
    source_url: "https://nmaahc.si.edu",
    logo_url: null,
    media_count: 10895,
  },
  {
    source_name: "flickr",
    display_name: "Flickr",
    source_url: "https://www.flickr.com",
    logo_url: null,
    media_count: 505849755,
  },
  {
    source_name: "met",
    display_name: "Metropolitan Museum of Art",
    source_url: "https://www.metmuseum.org",
    logo_url: null,
    media_count: 396650,
  },
]

const imageProviderNames = [
  "smithsonian_african_american_history_museum",
  "flickr",
  "met",
]

const meta = {
  title: "Components/VCollectionHeader",
  component: VCollectionHeader,
}

export default meta
type Story = StoryObj<typeof meta>

const collections = [
  {
    collectionName: "tag",
    collectionParams: {
      collection: "tag",
      tag: "cat",
    },
    mediaType: "image",
  },
  {
    collectionName: "source",
    collectionParams: {
      collection: "source",
      source: "met",
    },
    mediaType: "image",
  },
  {
    collectionName: "creator",
    collectionParams: {
      collection: "creator",
      source: "flickr",
      creator: "iocyoungreporters",
    },
    mediaType: "image",
    creatorUrl: "https://www.flickr.com/photos/126018610@N05",
  },
  {
    collectionName: "source-with-long-name",
    collectionParams: {
      collection: "source",
      source: "smithsonian_african_american_history_museum",
    },
    mediaType: "image",
  },
]

export const AllCollections: Omit<Story, "args"> = {
  render: () => ({
    components: { VCollectionHeader },
    setup() {
      const providerStore = useProviderStore()
      providerStore.$patch({
        providers: { image: imageProviders },
        sourceNames: { image: imageProviderNames },
      })
      const mediaStore = useMediaStore()
      mediaStore.$patch({
        results: { image: { count: 240 } },
        mediaFetchState: {
          image: { status: "success", error: null },
          audio: { status: "success", error: null },
        },
      })
      return () =>
        h(
          "div",
          { class: "wrapper w-full p-3 flex flex-col gap-4 bg-surface" },
          collections.map((collection) =>
            h(VCollectionHeader, {
              ...(collection as typeof VCollectionHeader.props),
              class: "bg-default",
            })
          )
        )
    },
  }),
  name: "All collections",
}
