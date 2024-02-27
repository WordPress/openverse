<template>
  <VCollectionResults
    v-if="collectionParams"
    kind="collection"
    :collection-params="collectionParams"
    :creator-url="creatorUrl"
    :collection-label="collectionLabel"
    :search-term="searchTerm"
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

import VCollectionResults from "~/components/VSearchResultsGrid/VCollectionResults.vue"

export default defineComponent({
  name: "VCollectionPage",
  components: {
    VCollectionResults,
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
      const params = props.collectionParams
      const key = `collection.ariaLabel.${params.collection}.${props.results.type}`
      return i18n.t(key, { ...params }).toString()
    })

    const searchTerm = computed(() => {
      if (props.collectionParams.collection === "creator") {
        return `${props.collectionParams.source}/${props.collectionParams.creator}`
      } else if (props.collectionParams.collection === "source") {
        return props.collectionParams.source
      } else {
        return props.collectionParams.tag
      }
    })

    return {
      collectionLabel,
      searchTerm,
    }
  },
})
</script>
