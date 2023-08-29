<template>
  <dl v-if="isSm" class="metadata grid gap-10" :style="columnCount">
    <div v-for="datum in metadata" :key="`${datum.label}`">
      <dt class="label-regular mb-2">{{ $t(datum.label) }}</dt>
      <VMetadataValue
        :datum="datum"
        @click="sendVisitSourceLinkEvent(datum.source)"
      />
    </div>
  </dl>
  <dl v-else class="grid grid-cols-[auto,1fr] gap-x-4 gap-y-6">
    <template v-for="datum in metadata">
      <dt :key="`${datum.label}`" class="label-regular">
        {{ $t(datum.label) }}
      </dt>
      <VMetadataValue
        :key="`${datum.label}-value`"
        :datum="datum"
        @click="sendVisitSourceLinkEvent(datum.source)"
      />
    </template>
  </dl>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import type { Metadata } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"
import { useUiStore } from "~/stores/ui"

import VMetadataValue from "~/components/VMediaInfo/VMetadataValue.vue"

export default defineComponent({
  name: "VMetadata",
  components: { VMetadataValue },
  props: {
    metadata: {
      type: Array as PropType<Metadata[]>,
      required: true,
    },
  },
  setup(props) {
    const route = useRoute()
    const uiStore = useUiStore()

    const isSm = computed(() => uiStore.isBreakpoint("sm"))

    const columnCount = computed(() => {
      // Audio page has a thumbnail, so it can fit fewer columns.
      const maxColumnCount = route.value.name?.includes("audio-id") ? 4 : 5
      return {
        "--column-count": Math.min(maxColumnCount, props.metadata.length),
      }
    })

    const { sendCustomEvent } = useAnalytics()
    const sendVisitSourceLinkEvent = (source?: string) => {
      if (!source) return
      sendCustomEvent("VISIT_SOURCE_LINK", {
        id: route.value.params.id,
        source,
      })
    }

    return {
      sendVisitSourceLinkEvent,
      isSm,
      columnCount,
    }
  },
})
</script>

<style scoped>
@screen sm {
  .metadata {
    grid-template-columns: repeat(
      var(--column-count, auto-fit),
      minmax(0, 10rem)
    );
  }
}
</style>
