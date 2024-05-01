<template>
  <VScrollableLine>
    <VSourceCreatorButton
      v-if="showCreator && creatorHref && media.creator"
      :href="creatorHref"
      icon-name="person"
      :title="media.creator"
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
    const showCreator = computed(() => {
      return Boolean(
        props.media.creator &&
          props.media.creator.toLowerCase() !== "unidentified"
      )
    })

    const searchStore = useSearchStore()

    const creatorHref = computed(() => {
      if (!props.media.creator) {
        return undefined
      }
      return searchStore.getCollectionPath({
        type: props.media.frontendMediaType,
        collectionParams: {
          collection: "creator",
          source: props.media.source,
          creator: props.media.creator,
        },
      })
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
      showCreator,
      creatorHref,
      sourceHref,
    }
  },
})
</script>
