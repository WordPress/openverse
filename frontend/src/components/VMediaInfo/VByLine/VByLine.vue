<template>
  <VScrollableLine>
    <VSourceCreatorButton
      v-if="showCreator && creatorHref && creator"
      :href="creatorHref"
      icon-name="person"
      :title="creator"
    />
    <VSourceCreatorButton
      :href="sourceHref"
      icon-name="institution"
      :title="sourceName"
    />
  </VScrollableLine>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType } from "vue"

import { useSearchStore } from "~/stores/search"
import type { SupportedMediaType } from "~/constants/media"

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
    creator: {
      type: String,
    },
    sourceName: {
      type: String,
      required: true,
    },
    sourceSlug: {
      type: String,
      required: true,
    },
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const showCreator = computed(() => {
      return Boolean(
        props.creator && props.creator.toLowerCase() !== "unidentified"
      )
    })

    const searchStore = useSearchStore()

    const creatorHref = computed(() => {
      if (!props.creator) {
        return undefined
      }
      return searchStore.getCollectionPath({
        type: props.mediaType,
        collectionParams: {
          collection: "creator",
          source: props.sourceSlug,
          creator: props.creator,
        },
      })
    })

    const sourceHref = computed(() => {
      return searchStore.getCollectionPath({
        type: props.mediaType,
        collectionParams: {
          collection: "source",
          source: props.sourceSlug,
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
