<template>
  <VScrollableLine>
    <VSourceCreatorButton
      v-if="creator"
      :title="creator.name"
      :href="creator.href"
      icon-name="person"
    />
    <VSourceCreatorButton
      :href="sourceHref"
      icon-name="institution"
      :title="media.sourceName"
    />
  </VScrollableLine>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType } from "vue"

import { useSearchStore } from "~/stores/search"
import type { AudioDetail, ImageDetail } from "~/types/media"

import VSourceCreatorButton from "~/components/VMediaInfo/VByLine/VSourceCreatorButton.vue"
import VScrollableLine from "~/components/VScrollableLine.vue"

/**
 * A link to a collection page, either a source or a creator.
 */
export default defineComponent({
  name: "VByLine",
  components: {
    VScrollableLine,
    VSourceCreatorButton,
  },
  props: {
    media: {
      type: Object as PropType<AudioDetail | ImageDetail>,
      required: true,
    },
  },
  setup(props) {
    const searchStore = useSearchStore()

    const creator = computed(() => {
      if (props.media.creator && props.media.creator !== "unidentified") {
        const href = searchStore.getCollectionPath({
          type: props.media.frontendMediaType,
          collectionParams: {
            collection: "creator",
            source: props.media.source,
            creator: props.media.creator,
          },
        })
        return { name: props.media.creator, href }
      }
      return null
    })

    const sourceHref = computed(() => {
      return searchStore.getCollectionPath({
        type: props.media.frontendMediaType,
        collectionParams: {
          collection: "source",
          source: props.media.source,
        },
      })
    })

    return {
      creator,
      sourceHref,
    }
  },
})
</script>
