import { useMediaStore } from "~/stores/media"
import { useProviderStore } from "~/stores/provider"

import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"

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

const AllCollectionsTemplate = (args) => ({
  template: `
<div class="wrapper w-full p-3 flex flex-col gap-4 bg-bg-surface">
    <VCollectionHeader v-for="collection in args.collections" :key="collection.collectionName" v-bind="collection" class="bg-bg"/>
</div>`,
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
    })
    return { args }
  },
})

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

export default {
  title: "Components/VCollectionHeader",
  component: VCollectionHeader,
}

export const AllCollections = {
  render: AllCollectionsTemplate.bind({}),
  name: "All collections",

  args: {
    collections,
  },
}
