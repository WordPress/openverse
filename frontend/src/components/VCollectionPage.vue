<template>
  <VMediaCollection
    v-if="collectionParams"
    :metadata="{ collectionParams, creatorUrl, kind: 'collection' }"
    :collection-label="collectionLabel"
    :results="results"
    class="p-6 pt-0 lg:p-10 lg:pt-2"
    @load-more="$emit('load-more')"
  />
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useI18n } from "~/composables/use-i18n"

import type { CollectionParams } from "~/types/search"
import type { Results } from "~/types/result"

import { defineEvent } from "~/types/emits"

import VMediaCollection from "~/components/VSearchResultsGrid/VMediaCollection.vue"

export default defineComponent({
  name: "VCollectionPage",
  components: {
    VMediaCollection,
  },
  props: {
    results: {
      type: Object as PropType<Results>,
      required: true,
    },
    collectionParams: {
      type: Object as PropType<CollectionParams>,
      required: true,
    },
    creatorUrl: {
      type: String,
    },
  },
  emits: {
    "load-more": defineEvent(),
  },
  setup(props) {
    const i18n = useI18n()

    const collectionLabel = computed(() => {
      const collection = props.collectionParams.collection
      const type = props.results.type
      switch (collection) {
        case "tag": {
          return i18n
            .t(`collection.ariaLabel.tag.${type}`, {
              tag: props.collectionParams.tag,
            })
            .toString()
        }
        case "source": {
          return i18n
            .t(`collection.ariaLabel.source.${type}`, {
              source: props.collectionParams.source,
            })
            .toString()
        }
        case "creator": {
          return i18n
            .t(`collection.ariaLabel.creator.${type}`, {
              creator: props.collectionParams.creator,
              source: props.collectionParams.source,
            })
            .toString()
        }
        default: {
          return ""
        }
      }
    })

    return {
      collectionLabel,
    }
  },
})
</script>
